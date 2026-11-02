"""Turn measurements into verdicts and plain-language meaning.

Classification rule (per memory dimension):
  delta = variant - baseline (medians)
  |delta| <= threshold          -> NEUTRAL
  delta < -threshold            -> REDUCES
  delta > +threshold            -> INCREASES

Thresholds:
  max RSS   max(2 pages, 2 x largest run-to-run spread, 0.5% of baseline)
            RSS is page-quantised and jittery (ASLR, allocator), so a change
            must clear both page granularity and observed noise.
  image     max(32 B, 0.5%)   deterministic, from the ELF file
  heap      max(64 B, 0.5%)   deterministic, from the tracked allocator
  stack     max(64 B, 2%)     deterministic, from the stack probe

Overall verdict = the resident (RSS) verdict if it moved; otherwise the
stack verdict ("stack only"); otherwise the image verdict ("image only").
A dimension that moves the opposite way is reported as a trade-off.
"""
from dataclasses import dataclass, field

REDUCES, INCREASES, NEUTRAL = "REDUCES", "INCREASES", "NEUTRAL"


@dataclass
class Dim:
    key: str
    label: str
    unit: str
    base: float
    var: float
    thr: float
    delta: float = 0.0
    pct: float = 0.0
    verdict: str = NEUTRAL

    def __post_init__(self):
        self.delta = self.var - self.base
        self.pct = (100.0 * self.delta / self.base) if self.base else 0.0
        if abs(self.delta) <= self.thr:
            self.verdict = NEUTRAL
        else:
            self.verdict = REDUCES if self.delta < 0 else INCREASES


@dataclass
class Outcome:
    test: object
    status: str = "done"            # done | skipped | failed
    reason: str = ""
    n: int = 0
    dims: dict = field(default_factory=dict)
    info: dict = field(default_factory=dict)
    overall: str = ""
    overall_word: str = ""
    tradeoffs: list = field(default_factory=list)
    checksum_match: object = None
    hypothesis: str = "n/a"
    meaning: str = ""
    base_meas: dict = None
    var_meas: dict = None
    base_build: object = None
    var_build: object = None
    extra: dict = field(default_factory=dict)   # scaling / limit / staged payloads


def _med(agg, key):
    v = agg.get(key) if agg else None
    return v["median"] if v else None


def rss_threshold(base, var, page_kb):
    spread = max(base["maxrss_kb"]["spread"], var["maxrss_kb"]["spread"])
    return max(2 * page_kb, 2 * spread, 0.005 * base["maxrss_kb"]["median"])


def compare(test, n, base_m, var_m, base_b, var_b, base_stack, var_stack, page_kb):
    oc = Outcome(test=test, n=n, base_meas=base_m, var_meas=var_m, base_build=base_b, var_build=var_b)
    oc.dims["rss"] = Dim("rss", "max RSS (time -v)", "KB", _med(base_m, "maxrss_kb"), _med(var_m, "maxrss_kb"),
                         rss_threshold(base_m, var_m, page_kb))
    bi, vi = base_b.static.get("image_b"), var_b.static.get("image_b")
    if bi is not None and vi is not None:
        oc.dims["image"] = Dim("image", "image text+data+bss", "B", bi, vi, max(32, 0.005 * bi))
    bh, vh = _med(base_m, "heap_peak_bytes"), _med(var_m, "heap_peak_bytes")
    if bh is not None and vh is not None:
        oc.dims["heap"] = Dim("heap", "tracked heap peak", "B", bh, vh, max(64, 0.005 * bh))
    if base_stack is not None and var_stack is not None:
        oc.dims["stack"] = Dim("stack", "stack high-water", "B", base_stack, var_stack, max(64, 0.02 * base_stack))

    oc.info["file"] = (base_b.static.get("file_b"), var_b.static.get("file_b"))
    oc.info["eh"] = (base_b.static.get("sec_eh_b"), var_b.static.get("sec_eh_b"))
    oc.info["minflt"] = (_med(base_m, "minflt"), _med(var_m, "minflt"))
    oc.info["time"] = (_med(base_m, "elapsed_s"), _med(var_m, "elapsed_s"))
    oc.info["su"] = (base_b.static.get("su_worst_frame_b"), var_b.static.get("su_worst_frame_b"))
    oc.info["anon"] = (_med(base_m, "rss_anon_kb"), _med(var_m, "rss_anon_kb"))

    # overall verdict
    rss = oc.dims["rss"]
    if rss.verdict != NEUTRAL:
        oc.overall_word, oc.overall = rss.verdict, f"{rss.verdict} (resident)"
    elif "stack" in oc.dims and oc.dims["stack"].verdict != NEUTRAL:
        oc.overall_word = oc.dims["stack"].verdict
        oc.overall = f"{oc.overall_word} (stack only)"
    elif "image" in oc.dims and oc.dims["image"].verdict != NEUTRAL:
        oc.overall_word = oc.dims["image"].verdict
        oc.overall = f"{oc.overall_word} (image only)"
    else:
        oc.overall_word = oc.overall = NEUTRAL
    for d in oc.dims.values():
        if oc.overall_word != NEUTRAL and d.verdict not in (NEUTRAL, oc.overall_word):
            oc.tradeoffs.append(f"{d.label} {d.verdict} ({fmt_delta(d)})")

    if test.same_output:
        oc.checksum_match = base_m.get("checksum") == var_m.get("checksum")
    if test.expect:
        oc.hypothesis = "CONFIRMED" if test.expect == oc.overall_word else "REFUTED"
    return oc


# ---------------------------------------------------------------------- #
def fmt_num(v, unit):
    if v is None:
        return "n/a"
    if unit == "KB":
        return f"{v:,.0f} KB" if abs(v) < 10240 else f"{v / 1024:,.1f} MB"
    if unit == "B":
        if abs(v) >= 1024 * 1024:
            return f"{v / 1048576:,.2f} MB"
        if abs(v) >= 10240:
            return f"{v / 1024:,.1f} KB"
        return f"{v:,.0f} B"
    if unit == "s":
        return f"{v:.3f} s"
    return f"{v:,.0f}"


def fmt_delta(d):
    sign = "+" if d.delta > 0 else ("-" if d.delta < 0 else "")
    return f"{sign}{fmt_num(abs(d.delta), d.unit)} ({d.pct:+.1f}%)"


def explain(oc, cfg, ctx):
    """Plain-language 'what does it mean' paragraph."""
    t = oc.test
    rss = oc.dims["rss"]
    parts = []
    if oc.overall_word == NEUTRAL:
        parts.append(f"No memory dimension moved beyond measurement noise (RSS threshold "
                     f"+/-{fmt_num(rss.thr, 'KB')}).")
    else:
        lead = {"resident": rss, "stack only": oc.dims.get("stack"), "image only": oc.dims.get("image")}
        key = oc.overall.split("(", 1)[1].rstrip(")")
        d = lead[key]
        verb = "lowers" if d.delta < 0 else "raises"
        parts.append(f"'{t.variant.label}' {verb} {d.label} by {fmt_num(abs(d.delta), d.unit)} "
                     f"({abs(d.pct):.1f}%) versus '{t.baseline.label}'.")
        if key != "resident":
            parts.append("Resident memory on Linux did not move measurably because demand paging only "
                         "charges pages that are touched and RSS is counted in whole pages.")
    if t.insight:
        parts.append(t.insight)

    if t.regime == "small":
        parts.append(f"Measured at N={oc.n:,} (code/runtime-dominated), this bounds what the lever can ever "
                     f"save; the process floor alone is {fmt_num(ctx.get('floor_kb'), 'KB')}.")
    else:
        parts.append(f"At N={oc.n:,} the baseline needs {fmt_num(rss.base, 'KB')} resident, so the change "
                     f"is {abs(rss.pct):.1f}% of what the Critter must provision.")
    im = oc.dims.get("image")
    if im and im.verdict != NEUTRAL and abs(im.delta) >= 64:
        parts.append(f"On an MMU-less microcontroller the image change ({fmt_delta(im)}) is paid in full in "
                     "flash/RAM, which Linux demand paging hides.")
    if oc.tradeoffs:
        parts.append("Trade-off: " + "; ".join(oc.tradeoffs) + ".")
    tb, tv = oc.info.get("time", (None, None))
    if tb and tv and tb > 0.02 and abs(tv - tb) / tb > 0.15:
        parts.append(f"Run time changed {100 * (tv - tb) / tb:+.0f}% ({tb:.3f} s -> {tv:.3f} s): a "
                     "memory/time trade-off to weigh, not ignore.")
    if oc.checksum_match is False:
        parts.append("WARNING: output checksum changed, so this optimisation altered the results; it is "
                     "not a free memory win.")
    if oc.hypothesis == "REFUTED":
        parts.append(f"Hypothesis ({t.expect}) refuted: worth a closer look in the report (check the "
                     "image breakdown in builds.log and the phase snapshots in phases.csv).")
    return " ".join(parts)


# ---------------------------------------------------------------------- #
def linear_fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return slope, my - slope * mx


def scaling_verdict(points, page_kb, budget_mb, rate_hz=100):
    """points: [(N, rss_kb)] -> dict with slope (B/sample), floor, bounded flag, uptime in budget."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    slope_kb, icpt = linear_fit(xs, ys)
    growth = slope_kb * (max(xs) - min(xs))
    bounded = growth <= max(4 * page_kb, 0.05 * max(icpt, 1))
    res = {"slope_b_per_sample": slope_kb * 1024, "floor_kb": icpt, "bounded": bounded}
    budget_kb = budget_mb * 1024
    if bounded:
        res["max_n"] = None
        res["verdict"] = "BOUNDED (memory independent of N)"
    else:
        max_n = (budget_kb - icpt) / slope_kb if slope_kb > 0 else None
        res["max_n"] = max_n
        hours = max_n / rate_hz / 3600 if max_n and max_n > 0 else 0
        res["verdict"] = (f"O(N): {slope_kb * 1024:,.1f} B/sample; a {budget_mb} MB budget holds "
                          f"~{max(max_n or 0, 0):,.0f} samples (~{hours:,.1f} h at {rate_hz} Hz)")
    return res
