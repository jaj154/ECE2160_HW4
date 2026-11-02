"""Execute unit binaries under `/usr/bin/time -v` and collect metrics.

Primary source (the assignment's requirement): GNU time -v, written to a
separate file with -o so it never mixes with the program's own output.

If GNU time is not installed, tools/ctime.c (a 60-line stand-in that
prints the same fields from the same wait4() rusage) is used instead and
the record is marked source=ctime.  Measuring through a small intermediate
process matters: max RSS survives exec(), so a child forked directly from
the Python harness would report the harness's own RSS as its floor.

Note on time -v fields: on Linux only 'Maximum resident set size' is
populated. 'Average resident set size', 'Average total size', 'Average stack
size' etc. are always 0 because the kernel does not provide integral RSS.
"""
import os
import re
import resource
import statistics
import subprocess
import tempfile
import threading
import time

TIME_FIELDS = {
    "Maximum resident set size (kbytes)": ("maxrss_kb", int),
    "Minor (reclaiming a frame) page faults": ("minflt", int),
    "Major (requiring I/O) page faults": ("majflt", int),
    "Voluntary context switches": ("vcsw", int),
    "Involuntary context switches": ("ivcsw", int),
    "User time (seconds)": ("user_s", float),
    "System time (seconds)": ("sys_s", float),
    "Swaps": ("swaps", int),
    "Page size (bytes)": ("page_bytes", int),
    "Exit status": ("exit_status", int),
}

RLIMITS = {"AS": resource.RLIMIT_AS, "STACK": resource.RLIMIT_STACK}


def parse_elapsed(text):
    secs = 0.0
    for part in text.strip().split(":"):
        secs = secs * 60 + float(part)
    return secs


def parse_gnu_time(text):
    rec = {}
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"Command terminated by signal (\d+)", line)
        if m:
            rec["signal"] = int(m.group(1))
            continue
        m = re.match(r"Command exited with non-zero status (\d+)", line)
        if m:
            rec["exit_status"] = int(m.group(1))
            continue
        if line.startswith("Elapsed (wall clock) time"):
            rec["elapsed_s"] = parse_elapsed(line.rsplit(": ", 1)[1])
            continue
        if ": " not in line:
            continue
        key, val = line.rsplit(": ", 1)
        if key in TIME_FIELDS:
            name, conv = TIME_FIELDS[key]
            try:
                rec[name] = conv(val)
            except ValueError:
                pass
    return rec


def parse_program_output(text):
    metrics, phases = {}, []
    for line in text.splitlines():
        if not line.startswith("@@"):
            continue
        if line.startswith("@@phase="):
            parts = line[2:].split()
            ph = {"name": parts[0].split("=", 1)[1]}
            for kv in parts[1:]:
                k, _, v = kv.partition("=")
                try:
                    ph[k] = float(v) if "." in v else int(v)
                except ValueError:
                    ph[k] = v
            phases.append(ph)
            continue
        k, _, v = line[2:].partition("=")
        try:
            metrics[k] = int(v)
        except ValueError:
            try:
                metrics[k] = float(v)
            except ValueError:
                metrics[k] = v
    return metrics, phases


def _status_of(rec):
    if rec.get("timeout"):
        return "timeout"
    if rec.get("signal"):
        sig = rec["signal"]
        return "SIGSEGV (stack overflow?)" if sig == 11 else f"signal {sig}"
    if rec.get("metrics", {}).get("error") == "oom":
        return "OOM"
    code = rec.get("exit_status", 0)
    if code:
        return "OOM" if code == 3 else f"exit {code}"
    return "ok"


class Runner:
    def __init__(self, env, repeats=5, no_aslr=False, timeout=600, log=None):
        self.env = env
        self.repeats = repeats
        self.timer = env["timer"]            # GNU time or the ctime helper
        self.timer_kind = env["timer_kind"]  # "gnu-time" | "ctime"
        self.setarch = [env["setarch"], env["machine"], "-R"] if (no_aslr and env.get("setarch")) else []
        self.timeout = timeout
        self.log = log
        self.cache = {}
        self.tmp = tempfile.mkdtemp(prefix="memlab_")

    # ------------------------------------------------------------------ #
    def run_once(self, exe, args=(), env=(), rlimits=(), tag=""):
        out_path = os.path.join(self.tmp, "stdout.txt")
        err_path = os.path.join(self.tmp, "stderr.txt")
        time_path = os.path.join(self.tmp, "time.txt")
        for p in (time_path,):
            if os.path.exists(p):
                os.remove(p)
        cmd = self.setarch + [exe] + list(args)
        if self.timer_kind == "gnu-time":
            cmd = [self.timer, "-v", "-o", time_path] + cmd
        else:
            cmd = [self.timer, "-o", time_path] + cmd
        run_env = dict(os.environ)
        run_env["LC_ALL"] = "C"
        run_env.update(dict(env))
        limits = [(RLIMITS[k], v) for k, v in rlimits]

        def preexec():
            for res_id, val in limits:
                _soft, hard = resource.getrlimit(res_id)
                if hard != resource.RLIM_INFINITY and val > hard:
                    val = hard
                resource.setrlimit(res_id, (val, hard))

        rec = {"tag": tag, "cmd": " ".join(cmd), "source": self.timer_kind}
        t0 = time.monotonic()
        with open(out_path, "w") as fo, open(err_path, "w") as fe:
            proc = subprocess.Popen(cmd, stdout=fo, stderr=fe, env=run_env,
                                    preexec_fn=preexec if limits else None)
            timer = threading.Timer(self.timeout, proc.kill)
            timer.start()
            try:
                proc.wait()
            finally:
                timer.cancel()
        wall = time.monotonic() - t0
        with open(out_path) as f:
            stdout = f.read()
        with open(err_path) as f:
            rec["stderr_tail"] = "\n".join(f.read().strip().splitlines()[-3:])
        rec["metrics"], rec["phases"] = parse_program_output(stdout)
        if os.path.exists(time_path):
            with open(time_path) as f:
                rec.update(parse_gnu_time(f.read()))
        else:
            rec["exit_status"] = proc.returncode if proc.returncode > 0 else 125
            rec["signal"] = -proc.returncode if proc.returncode < 0 else 0
        if wall >= self.timeout:
            rec["timeout"] = True
        rec["status"] = _status_of(rec)
        rec["ok"] = rec["status"] == "ok"
        if self.log:
            self.log.raw_run(rec)
        return rec

    # ------------------------------------------------------------------ #
    def measure(self, exe, args=(), env=(), rlimits=(), repeats=None, tag=""):
        """Run `repeats` times; return aggregate dict (cached per config)."""
        repeats = repeats or self.repeats
        key = (exe, tuple(args), tuple(env), tuple(rlimits), repeats)
        if key in self.cache:
            return self.cache[key]
        runs = [self.run_once(exe, args, env, rlimits, tag=f"{tag}#{i + 1}") for i in range(repeats)]
        agg = aggregate(runs)
        self.cache[key] = agg
        return agg

    def stack_probe(self, exe, args=(), env=(), probe_kb=1024):
        key = ("probe", exe, tuple(args), tuple(env), probe_kb)
        if key in self.cache:
            return self.cache[key]
        e = tuple(env) + (("CRITTER_PROBE_KB", str(probe_kb)),)
        rec = self.run_once(exe, args, e, (), tag="stack-probe")
        val = rec["metrics"].get("stack_hwm_bytes") if rec["ok"] else None
        self.cache[key] = val
        return val


def aggregate(runs):
    ok = [r for r in runs if r["ok"]]
    agg = {"runs": runs, "n_runs": len(runs), "n_ok": len(ok),
           "status": "ok" if len(ok) == len(runs) else (runs[-1]["status"] if not ok else "partial")}
    if not ok:
        return agg

    def stats(key, src=None):
        vals = [(r["metrics"] if src == "m" else r).get(key) for r in ok]
        vals = [v for v in vals if isinstance(v, (int, float))]
        if not vals:
            return None
        return {"median": statistics.median(vals), "min": min(vals), "max": max(vals),
                "spread": max(vals) - min(vals)}

    for k in ("maxrss_kb", "minflt", "majflt", "elapsed_s", "user_s", "sys_s", "vcsw", "ivcsw"):
        agg[k] = stats(k)
    for k in ("heap_peak_bytes", "heap_allocs", "vm_stk_kb", "vm_data_kb", "vm_peak_kb",
              "rss_anon_kb", "rss_file_kb", "malloc_arena_bytes", "malloc_mmap_bytes"):
        agg[k] = stats(k, "m")
    agg["checksum"] = ok[0]["metrics"].get("checksum")
    agg["checksums_stable"] = len({r["metrics"].get("checksum") for r in ok}) == 1
    agg["phases"] = ok[0]["phases"]
    agg["metrics"] = ok[0]["metrics"]
    return agg
