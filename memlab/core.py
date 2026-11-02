"""The lab orchestrator: build, run, analyse and report every TestCase."""
import os
import time

from .analysis import Dim, Outcome, compare, explain, fmt_num, rss_threshold, scaling_verdict
from .build import BuildSpec
from .testcases import SUITE_ORDER, SUITE_TITLES, Variant


class Lab:
    def __init__(self, cfg, env, builder, runner, reporter):
        self.cfg, self.env, self.b, self.r, self.rep = cfg, env, builder, runner, reporter
        self.page_kb = env["page_bytes"] / 1024
        self.floor_kb = None

    # ------------------------------------------------------------------ #
    def n_for(self, t):
        if t.n_override:
            return t.n_override
        return self.cfg["n_small"] if t.regime == "small" else self.cfg["n_large"]

    def measure_floor(self):
        res = self.b.build(BuildSpec("noop"))
        if not res.ok:
            raise SystemExit(f"Cannot build even the empty program:\n{res.error}")
        self.rep.current_tag = "FLOOR"
        agg = self.r.measure(res.exe, (), tag="noop")
        if not agg["n_ok"]:
            raise SystemExit("The empty program failed to run; check the toolchain.")
        self.floor_kb = agg["maxrss_kb"]["median"]
        return self.floor_kb

    def run(self, tests):
        for suite in SUITE_ORDER:
            group = [t for t in tests if t.suite == suite]
            if not group:
                continue
            self.rep.suite_banner(suite, SUITE_TITLES[suite], len(group))
            for t in group:
                self.rep.current_tag = t.tid
                handler = {"compare": self.run_compare, "scaling": self.run_scaling,
                           "limit": self.run_limit, "staged": self.run_staged}[t.kind]
                try:
                    handler(t)
                except Exception as e:  # never let one test kill a long run
                    oc = Outcome(test=t, status="failed", reason=f"harness error: {e!r}")
                    self.rep.compare_block(oc)

    # ------------------------------------------------------------------ #
    def _build_pair(self, t):
        self.rep.progress(f"{t.tid}: building")
        bb, vb = self.b.build(t.baseline.spec()), self.b.build(t.variant.spec())
        if not bb.ok:
            return bb, vb, f"baseline build failed: {bb.error.splitlines()[-1] if bb.error else ''}"
        if not vb.ok:
            first = next((l for l in vb.error.splitlines() if "error" in l), vb.error.splitlines()[-1] if vb.error else "")
            return bb, vb, f"build failed (unsupported here?): {first.strip()[:120]}"
        return bb, vb, ""

    def _probe(self, variant, n):
        pb = self.b.build(variant.spec(probe=True))
        if not pb.ok:
            return None
        return self.r.stack_probe(pb.exe, variant.argv(n), variant.env, self.cfg["probe_kb"])

    def run_compare(self, t):
        n = self.n_for(t)
        bb, vb, err = self._build_pair(t)
        if err:
            return self.rep.compare_block(Outcome(test=t, status="skipped", reason=err, n=n))
        self.rep.progress(f"{t.tid}: running baseline x{self.r.repeats}")
        bm = self.r.measure(bb.exe, t.baseline.argv(n), t.baseline.env, t.baseline.rlimits, tag="base")
        self.rep.progress(f"{t.tid}: running variant x{self.r.repeats}")
        vm = self.r.measure(vb.exe, t.variant.argv(n), t.variant.env, t.variant.rlimits, tag="var")
        if not bm["n_ok"]:
            return self.rep.compare_block(Outcome(test=t, status="failed", n=n,
                                                  reason=f"baseline run failed: {bm['status']}"))
        if not vm["n_ok"]:
            tail = vm["runs"][-1].get("stderr_tail", "").splitlines()
            return self.rep.compare_block(Outcome(test=t, status="skipped", n=n,
                                                  reason=f"variant run failed: {vm['status']} "
                                                         f"{tail[-1][:80] if tail else ''}"))
        bs = vs = None
        if t.measure_stack and self.cfg["stack_probe"]:
            self.rep.progress(f"{t.tid}: stack probe")
            bs, vs = self._probe(t.baseline, n), self._probe(t.variant, n)
        oc = compare(t, n, bm, vm, bb, vb, bs, vs, self.page_kb)
        oc.meaning = explain(oc, self.cfg, {"floor_kb": self.floor_kb})
        self.rep.compare_block(oc)

    # ------------------------------------------------------------------ #
    def run_scaling(self, t):
        ns = self.cfg["scaling_ns"]
        reps = min(3, self.r.repeats)
        table, fits = {}, {}
        for v in t.variants:
            res = self.b.build(v.spec())
            row = []
            for n in ns:
                self.rep.progress(f"{t.tid}: {v.label} N={n:,}")
                agg = self.r.measure(res.exe, v.argv(n), v.env, v.rlimits, repeats=reps, tag=f"{v.label}@{n}") \
                    if res.ok else {"n_ok": 0}
                row.append(agg["maxrss_kb"]["median"] if agg.get("n_ok") else None)
            table[v.label] = row
            pts = [(n, kb) for n, kb in zip(ns, row) if kb]
            fits[v.label] = scaling_verdict(pts, self.page_kb, self.cfg["budget_mb"]) if len(pts) >= 2 else \
                {"verdict": "insufficient data", "slope_b_per_sample": None}
        oc = Outcome(test=t, n=max(ns), extra={"ns": ns, "table": table, "fits": fits})
        slopes = {k: f["slope_b_per_sample"] for k, f in fits.items() if f.get("slope_b_per_sample") is not None}
        parts = []
        if len(slopes) >= 2:
            worst = max(slopes, key=slopes.get)
            best = min(slopes, key=slopes.get)
            ratio = (slopes[worst] / slopes[best]) if slopes[best] > 0.5 else None
            parts.append(f"'{worst}' costs {slopes[worst]:,.1f} bytes per sample retained, '{best}' "
                         f"{max(slopes[best], 0):,.1f}" + (f" ({ratio:,.0f}x less)." if ratio else " (effectively flat)."))
        parts.append(t.insight)
        oc.overall = "; ".join(f"{k}: {f['verdict']}" for k, f in fits.items())
        oc.meaning = " ".join(parts)
        self.rep.scaling_block(oc)

    # ------------------------------------------------------------------ #
    def run_limit(self, t):
        n = self.n_for(t)
        rows = []
        for v in t.variants:
            self.rep.progress(f"{t.tid}: {v.label}")
            res = self.b.build(v.spec())
            if not res.ok:
                rows.append({"label": v.label, "status": "build failed", "rss": None})
                continue
            agg = self.r.measure(res.exe, v.argv(n), v.env, v.rlimits, repeats=1, tag=v.label)
            run = agg["runs"][0]
            rows.append({"label": v.label, "status": run["status"],
                         "rss": run.get("maxrss_kb") if run["ok"] else None})
        passed = [r["label"] for r in rows if r["status"] == "ok"]
        failed = [r["label"] for r in rows if r["status"] != "ok"]
        oc = Outcome(test=t, n=n, extra={"rows": rows})
        oc.overall = f"PASS: {', '.join(passed) or 'none'}   |   FAIL: {', '.join(failed) or 'none'}"
        oc.meaning = (f"Of {len(rows)} configurations, {len(passed)} fit the limit. " + t.insight)
        self.rep.limit_block(oc)

    # ------------------------------------------------------------------ #
    def run_staged(self, t):
        n = self.n_for(t)
        bb = self.b.build(t.baseline.spec())
        if not bb.ok:
            return self.rep.staged_block(Outcome(test=t, status="skipped", reason="baseline build failed", n=n))
        bm = self.r.measure(bb.exe, t.baseline.argv(n), t.baseline.env, (), tag="base")
        prefix = os.path.join(self.r.tmp, "handoff")
        stages, worst, last = [], None, None
        for st in ("acquire", "clean", "predict"):
            v = Variant(f"stage={st}", "pipeline", args=(("stage", st), ("handoff", prefix)))
            self.rep.progress(f"{t.tid}: stage {st}")
            agg = self.r.measure(bb.exe, v.argv(n), (), (), tag=f"stage-{st}")
            if not agg["n_ok"]:
                return self.rep.staged_block(Outcome(test=t, status="failed", n=n,
                                                     reason=f"stage {st} failed: {agg['status']}"))
            kb = agg["maxrss_kb"]["median"]
            stages.append((f"process {len(stages) + 1}: {st}", kb))
            if worst is None or kb > worst["maxrss_kb"]["median"]:
                worst = agg
            last = agg
        for ext in (".raw", ".clean"):
            try:
                os.remove(prefix + ext)
            except OSError:
                pass
        t.variant = Variant("one process per phase", "pipeline")
        oc = Outcome(test=t, n=n, base_meas=bm, var_meas=worst, extra={"stages": stages})
        oc.dims["rss"] = Dim("rss", "max RSS (time -v)", "KB", bm["maxrss_kb"]["median"],
                             worst["maxrss_kb"]["median"], rss_threshold(bm, worst, self.page_kb))
        d = oc.dims["rss"]
        oc.overall_word = d.verdict
        oc.overall = f"{d.verdict} (resident)" if d.verdict != "NEUTRAL" else "NEUTRAL"
        oc.checksum_match = bm.get("checksum") == last.get("checksum")
        oc.hypothesis = "CONFIRMED" if t.expect == d.verdict else "REFUTED"
        oc.meaning = explain(oc, self.cfg, {"floor_kb": self.floor_kb})
        self.rep.staged_block(oc)
