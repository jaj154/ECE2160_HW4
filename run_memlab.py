#!/usr/bin/env python3
"""Critter Memory Lab -- what are the biggest impacts to memory usage?

Examples
  python3 run_memlab.py                      # everything (default sizes)
  python3 run_memlab.py --quick              # smaller N, 3 repeats: a fast first look
  python3 run_memlab.py --suite algo,overlay # selected suites
  python3 run_memlab.py --only F-COM,S-      # tests whose id starts with these
  python3 run_memlab.py --list               # list all tests and hypotheses
  python3 run_memlab.py --repeats 10 --no-aslr   # report-quality numbers
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from memlab.build import Builder  # noqa: E402
from memlab.core import Lab  # noqa: E402
from memlab.env import probe_environment  # noqa: E402
from memlab.report import Reporter  # noqa: E402
from memlab.runner import Runner  # noqa: E402
from memlab.testcases import SUITE_ORDER, build_all  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--quick", action="store_true", help="N_large=200k, 3 repeats")
    p.add_argument("--suite", default=",".join(SUITE_ORDER), help=f"comma list from: {','.join(SUITE_ORDER)}")
    p.add_argument("--only", default="", help="comma list of test ids or id prefixes (e.g. F-MEM,G-01)")
    p.add_argument("--units", default="io,mem,compute", help="units included in the flag suite")
    p.add_argument("--repeats", type=int, default=None, help="runs per configuration (default 5, quick 3)")
    p.add_argument("--n-small", type=int, default=20_000, help="samples for code-dominated tests")
    p.add_argument("--n-large", type=int, default=None, help="samples for data-dominated tests (default 1M)")
    p.add_argument("--budget-mb", type=int, default=None, help="address-space budget for the budget suite")
    p.add_argument("--stack-limit-kb", type=int, default=128, help="stack rlimit for the stack-budget test")
    p.add_argument("--probe-kb", type=int, default=1024, help="stack region painted by the probe build")
    p.add_argument("--no-stack-probe", action="store_true", help="skip stack high-water measurements")
    p.add_argument("--no-aslr", action="store_true", help="run binaries under 'setarch -R'")
    p.add_argument("--cc", default=os.environ.get("CC", "gcc"))
    p.add_argument("--logdir", default=os.path.join(HERE, "logs"))
    p.add_argument("--builddir", default=os.path.join(HERE, "build"))
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--list", action="store_true", help="list tests and exit")
    return p.parse_args()


def make_cfg(a):
    n_large = a.n_large or (200_000 if a.quick else 1_000_000)
    repeats = a.repeats or (3 if a.quick else 5)
    budget = a.budget_mb or max(16, int(round(64 * n_large / 1e6)))
    return {"repeats": repeats, "n_small": a.n_small, "n_large": n_large,
            "scaling_ns": [n_large // 8, n_large // 4, n_large // 2, n_large],
            "budget_mb": budget, "stack_limit_kb": a.stack_limit_kb, "probe_kb": a.probe_kb,
            "stack_probe": not a.no_stack_probe, "flag_units": a.units.split(","), "no_aslr": a.no_aslr}


def setup_timer(env, a):
    """Use GNU time if present; otherwise build tools/ctime.c (same output fields)."""
    if env["gnu_time"]:
        env["timer"], env["timer_kind"] = env["gnu_time"], "gnu-time"
        return True
    os.makedirs(a.builddir, exist_ok=True)
    exe = os.path.join(a.builddir, "ctime")
    src = os.path.join(HERE, "tools", "ctime.c")
    rc = subprocess.run([a.cc, "-O2", "-o", exe, src], capture_output=True, text=True)
    env["timer"], env["timer_kind"] = exe, "ctime"
    return rc.returncode == 0


def main():
    a = parse_args()
    cfg = make_cfg(a)
    suites = [s.strip() for s in a.suite.split(",") if s.strip()]
    bad = [s for s in suites if s not in SUITE_ORDER]
    if bad:
        sys.exit(f"unknown suite(s): {bad}; choose from {SUITE_ORDER}")
    tests = build_all(cfg, suites, [x for x in a.only.split(",") if x] or None)

    if a.list:
        for t in tests:
            print(f"{t.tid:<12} {t.suite:<8} {t.kind:<8} expect={t.expect or '-':<10} {t.title}")
        print(f"\n{len(tests)} tests")
        return

    stamp = time.strftime("%Y%m%d_%H%M%S")
    rep = Reporter(os.path.join(a.logdir, f"memlab_{stamp}"), color=not a.no_color)
    env = probe_environment(a.cc)
    if not setup_timer(env, a):
        sys.exit("No GNU time and the ctime helper failed to build; install GNU time: sudo apt install time")
    builder = Builder(os.path.join(HERE, "src"), a.builddir, a.cc, log=rep)
    runner = Runner(env, repeats=cfg["repeats"], no_aslr=a.no_aslr, log=rep)
    lab = Lab(cfg, env, builder, runner, rep)

    t0 = time.time()
    floor = lab.measure_floor()
    rep.header(env, cfg, floor)
    rep.out(f"  Running {len(tests)} tests ...")
    try:
        lab.run(tests)
    except KeyboardInterrupt:
        rep.out("\n  Interrupted -- writing partial results.")
    rep.final_summary(env, cfg, floor, t0)


if __name__ == "__main__":
    main()
