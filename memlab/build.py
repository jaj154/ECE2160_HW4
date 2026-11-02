"""Compile one binary per configuration and measure its static footprint.

Static ("image") metrics come from the ELF file, not from running it:
  text   .text + .rodata + .eh_frame + ...  (code and read-only data)
  data   initialised writable data
  bss    zero-initialised data (reserved, costs RAM only when touched on Linux,
         but is allocated in full at boot on an MMU-less microcontroller)
  image  text + data + bss  -- the number an MCU linker script must fit
Also recorded: .eh_frame (unwind tables), file size on disk (includes symbols
and debug info that are never loaded), worst stack frame from -fstack-usage,
and the largest symbols from nm.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

COMMON = ["critter_common.c", "critter_algo.c"]
UNIT_SOURCES = {
    "noop": ["noop.c", "critter_common.c"],
    "io": ["unit_io.c"] + COMMON,
    "mem": ["unit_mem.c"] + COMMON,
    "compute": ["unit_compute.c"] + COMMON,
    "pipeline": ["pipeline.c"] + COMMON,
}

# Fixed for every build so that only the flag under test changes.
#  -ffp-contract=off : keeps FP results identical across -O levels, which
#                      makes the output checksum a valid correctness check.
FIXED_CFLAGS = ["-std=gnu11", "-Wall", "-Wno-unused-function", "-ffp-contract=off"]
# Analysis-only: -fstack-usage writes .su files and does not change codegen;
# -Wl,-Map writes a linker map and does not change the binary.
ANALYSIS_CFLAGS = ["-fstack-usage"]


@dataclass(frozen=True)
class BuildSpec:
    unit: str
    cflags: tuple = ("-O2",)
    ldflags: tuple = ()
    defines: tuple = ()          # (("NAME", "VALUE"), ...)
    probe: bool = False          # -DCRITTER_STACK_PROBE build (stack metric only)

    def key(self, src_hash):
        blob = json.dumps([self.unit, self.cflags, self.ldflags, self.defines, self.probe, src_hash])
        return hashlib.sha1(blob.encode()).hexdigest()

    def describe(self):
        parts = list(self.cflags) + list(self.ldflags) + [f"-D{k}={v}" for k, v in self.defines]
        return " ".join(parts) if parts else "(none)"


@dataclass
class BuildResult:
    ok: bool
    spec: BuildSpec
    exe: str = ""
    cmd: str = ""
    error: str = ""
    warnings: str = ""
    compile_s: float = 0.0
    static: dict = field(default_factory=dict)

    def to_json(self):
        return {"ok": self.ok, "exe": self.exe, "cmd": self.cmd, "error": self.error,
                "warnings": self.warnings, "compile_s": self.compile_s, "static": self.static}


def _sources_hash(src_dir):
    h = hashlib.sha1()
    for p in sorted(Path(src_dir).glob("*.[ch]")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _run(cmd, cwd=None, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def berkeley_size(exe):
    out = _run(["size", exe])
    lines = out.stdout.strip().splitlines()
    if out.returncode != 0 or len(lines) < 2:
        return {}
    text, data, bss, dec = (int(x) for x in lines[1].split()[:4])
    return {"text_b": text, "data_b": data, "bss_b": bss, "image_b": dec}


def sysv_sections(exe):
    out = _run(["size", "-A", exe])
    sec = {}
    for line in out.stdout.splitlines():
        m = re.match(r"^(\.\S+)\s+(\d+)\s+\d+", line.strip())
        if m:
            sec[m.group(1)] = int(m.group(2))
    return {
        "sec_text_b": sec.get(".text", 0),
        "sec_rodata_b": sec.get(".rodata", 0),
        "sec_eh_b": sec.get(".eh_frame", 0) + sec.get(".eh_frame_hdr", 0),
        "sec_reloc_b": sec.get(".rela.dyn", 0) + sec.get(".rela.plt", 0),
        "sec_bss_b": sec.get(".bss", 0),
    }


def top_symbols(exe, k=5):
    out = _run(["nm", "--size-sort", "-S", "--radix=d", exe])
    if out.returncode != 0:
        return []
    syms = []
    for line in out.stdout.strip().splitlines()[-k:][::-1]:
        parts = line.split()
        if len(parts) >= 4:
            syms.append(f"{parts[3]}({int(parts[1])}B,{parts[2]})")
    return syms


def stack_usage(bdir):
    """Worst single frame reported by -fstack-usage (.su files)."""
    worst, worst_fn, n_dynamic = 0, "", 0
    for su in Path(bdir).rglob("*.su"):
        for line in su.read_text(errors="replace").splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            try:
                b = int(parts[1])
            except ValueError:
                continue
            if "dynamic" in parts[2]:
                n_dynamic += 1
            if b > worst:
                worst, worst_fn = b, parts[0].rsplit(":", 1)[-1]
    return {"su_worst_frame_b": worst, "su_worst_fn": worst_fn, "su_dynamic_frames": n_dynamic}


class Builder:
    def __init__(self, src_dir, build_root, cc="gcc", log=None):
        self.src = Path(src_dir).resolve()
        self.root = Path(build_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.cc = cc
        self.log = log
        self.src_hash = _sources_hash(self.src)
        self.cache = {}
        self.have_size = shutil.which("size") is not None
        self.have_nm = shutil.which("nm") is not None

    def build(self, spec: BuildSpec) -> BuildResult:
        key = spec.key(self.src_hash)
        if key in self.cache:
            return self.cache[key]
        bdir = self.root / f"{spec.unit}{'_probe' if spec.probe else ''}_{key[:12]}"
        meta = bdir / "build.json"
        exe = bdir / spec.unit
        if meta.exists() and exe.exists():
            d = json.loads(meta.read_text())
            res = BuildResult(ok=d["ok"], spec=spec, exe=d["exe"], cmd=d["cmd"], error=d["error"],
                              warnings=d.get("warnings", ""), compile_s=d["compile_s"], static=d["static"])
            self.cache[key] = res
            return res

        if bdir.exists():
            shutil.rmtree(bdir)
        bdir.mkdir(parents=True)
        defines = [f"-D{k}={v}" for k, v in spec.defines]
        if spec.probe:
            defines.append("-DCRITTER_STACK_PROBE")
        srcs = [str(self.src / f) for f in UNIT_SOURCES[spec.unit]]
        cmd = ([self.cc] + FIXED_CFLAGS + list(spec.cflags) + ANALYSIS_CFLAGS + defines +
               [f"-I{self.src}"] + srcs + ["-o", spec.unit] + list(spec.ldflags) +
               ["-lm", f"-Wl,-Map={spec.unit}.map"])
        t0 = time.monotonic()
        try:
            out = _run(cmd, cwd=bdir)
            ok, err = out.returncode == 0, out.stderr
        except (OSError, subprocess.SubprocessError) as e:
            ok, err = False, str(e)
        dt = time.monotonic() - t0
        res = BuildResult(ok=ok, spec=spec, exe=str(exe), cmd=" ".join(cmd), compile_s=round(dt, 3))
        if not ok:
            res.error = "\n".join(err.strip().splitlines()[-6:])
        else:
            res.warnings = "\n".join(l for l in err.splitlines() if "warning" in l)[:2000]
            st = {"file_b": os.path.getsize(exe)}
            if self.have_size:
                st.update(berkeley_size(str(exe)))
                st.update(sysv_sections(str(exe)))
            if self.have_nm:
                st["top_symbols"] = top_symbols(str(exe))
            st.update(stack_usage(bdir))
            res.static = st
        meta.write_text(json.dumps(res.to_json(), indent=1))
        if self.log:
            self.log.build_record(res)
        self.cache[key] = res
        return res
