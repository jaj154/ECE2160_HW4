"""Platform probing: everything a reviewer needs to reproduce the numbers.

Memory results are only meaningful with their context: page size (Pi 5
kernels use 16 KB pages, which quantizes RSS), compiler and libc versions
(glibc's qsort and malloc policies changed between releases), CPU governor
(affects timing, not memory) and ASLR (adds run-to-run RSS jitter).
"""
import os
import platform
import resource
import shutil
import subprocess


def _read(path, default=""):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read().strip().strip("\x00")
    except OSError:
        return default


def _cmd_first_line(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        text = (out.stdout or out.stderr).strip().splitlines()
        return text[0] if text else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def probe_environment(cc="gcc"):
    env = {}
    env["machine"] = platform.machine()
    env["kernel"] = platform.release()
    osr = _read("/etc/os-release")
    env["os"] = next((l.split("=", 1)[1].strip('"') for l in osr.splitlines()
                      if l.startswith("PRETTY_NAME=")), platform.system())
    env["model"] = (_read("/proc/device-tree/model") or
                    _read("/sys/firmware/devicetree/base/model") or "unknown (not a device-tree board)")
    env["is_pi5"] = "Raspberry Pi 5" in env["model"]
    env["page_bytes"] = os.sysconf("SC_PAGE_SIZE")
    env["cpus"] = os.cpu_count()
    meminfo = _read("/proc/meminfo")
    for line in meminfo.splitlines():
        if line.startswith("MemTotal:"):
            env["mem_total_kb"] = int(line.split()[1])
    env["governor"] = _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "n/a")
    env["aslr"] = _read("/proc/sys/kernel/randomize_va_space", "n/a")
    soft, _hard = resource.getrlimit(resource.RLIMIT_STACK)
    env["stack_rlimit_kb"] = "unlimited" if soft == resource.RLIM_INFINITY else soft // 1024
    env["cc"] = cc
    env["cc_version"] = _cmd_first_line([cc, "--version"])
    try:
        env["libc"] = os.confstr("CS_GNU_LIBC_VERSION")
    except (ValueError, OSError):
        env["libc"] = " ".join(platform.libc_ver())
    env["python"] = platform.python_version()

    gnu_time = shutil.which("time", path="/usr/bin:/bin") or ("/usr/bin/time" if os.path.exists("/usr/bin/time") else None)
    if gnu_time:
        ver = _cmd_first_line([gnu_time, "--version"])
        if "GNU" not in ver:
            gnu_time = None
        env["gnu_time_version"] = ver
    env["gnu_time"] = gnu_time
    env["setarch"] = shutil.which("setarch")
    env["size_tool"] = shutil.which("size")
    env["nm_tool"] = shutil.which("nm")

    warnings = []
    if not gnu_time:
        warnings.append("GNU time not found: using tools/ctime, which reports the same kernel rusage "
                        "fields. Install GNU time for the assignment's 'time -v' numbers:  sudo apt install time")
    if not env["is_pi5"]:
        warnings.append(f"Host is '{env['model']}' ({env['machine']}), not a Raspberry Pi 5. "
                        "Absolute numbers will differ from the target; relative conclusions usually hold.")
    if env["governor"] not in ("performance", "n/a"):
        warnings.append(f"CPU governor is '{env['governor']}'. Memory is unaffected, but timing columns "
                        "are noisier. For timing: echo performance | sudo tee "
                        "/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
    if env["aslr"] == "2":
        warnings.append("ASLR is on (normal). It adds small run-to-run RSS jitter; use --no-aslr to "
                        "run every binary under 'setarch -R'.")
    if not env["size_tool"] or not env["nm_tool"]:
        warnings.append("binutils 'size'/'nm' missing: image-size metrics disabled (sudo apt install binutils)")
    env["warnings"] = warnings
    return env
