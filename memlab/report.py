"""Terminal output and log files.

Every run creates logs/memlab_<timestamp>/ containing:
  console.log    exact copy of the terminal output (no colour codes)
  summary.md     report-ready summary: environment, verdict tables, biggest
                 impacts, scaling and budget results, per-test write-ups
  results.csv    one row per test, every metric, verdict and meaning
  results.json   the same, machine-readable, plus phase snapshots
  runs_raw.csv   every individual execution (for error bars / plots)
  phases.csv     in-process RSS/heap snapshots at each phase boundary
  builds.log     compiler command, image breakdown, largest symbols, worst
                 stack frame for every binary built
"""
import csv
import json
import os
import re
import sys
import textwrap
import time

from .analysis import INCREASES, NEUTRAL, REDUCES, fmt_delta, fmt_num

WIDTH = 100
ANSI = {"REDUCES": "\033[32m", "INCREASES": "\033[31m", "NEUTRAL": "\033[90m", "SKIP": "\033[33m",
        "PASS": "\033[32m", "FAIL": "\033[31m", "bold": "\033[1m", "head": "\033[36m", "reset": "\033[0m"}
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def lead_dim(o):
    """The dimension that decided the overall verdict (RSS when neutral)."""
    if "(stack only)" in o.overall:
        return o.dims["stack"]
    if "(image only)" in o.overall:
        return o.dims["image"]
    return o.dims["rss"]


class Reporter:
    def __init__(self, logdir, color=True):
        self.dir = logdir
        os.makedirs(logdir, exist_ok=True)
        self.color = color and sys.stdout.isatty()
        self.console = open(os.path.join(logdir, "console.log"), "w")
        self.builds = open(os.path.join(logdir, "builds.log"), "w")
        self.raw_f = open(os.path.join(logdir, "runs_raw.csv"), "w", newline="")
        self.raw = csv.writer(self.raw_f)
        self.raw.writerow(["tag", "status", "source", "maxrss_kb", "minflt", "majflt",
                           "elapsed_s", "user_s", "sys_s", "vcsw", "ivcsw", "heap_peak_bytes", "vm_stk_kb",
                           "rss_anon_kb", "rss_file_kb", "checksum", "cmd"])
        self.ph_f = open(os.path.join(logdir, "phases.csv"), "w", newline="")
        self.ph = csv.writer(self.ph_f)
        self.ph.writerow(["tag", "phase", "vmrss_kb", "vmhwm_kb", "heap_cur", "heap_peak", "t_s"])
        self.outcomes = []
        self.current_tag = ""

    # -------------------------------------------------------------- output
    def c(self, text, key):
        return f"{ANSI[key]}{text}{ANSI['reset']}" if self.color and key in ANSI else text

    def out(self, line=""):
        print(line, flush=True)
        self.console.write(_ANSI_RE.sub("", line) + "\n")
        self.console.flush()

    def wrap(self, label, text, indent=13):
        lines = textwrap.wrap(text, WIDTH - indent) or [""]
        self.out(f"  {label:<10}: {lines[0]}")
        for l in lines[1:]:
            self.out(" " * indent + l)

    def verdict(self, v):
        word = v.split()[0] if v else ""
        return self.c(v, word if word in ANSI else "bold")

    # -------------------------------------------------------------- hooks
    def build_record(self, res):
        b = self.builds
        b.write(f"=== {res.spec.unit}{' [probe]' if res.spec.probe else ''}  {res.spec.describe()}\n")
        b.write(f"cmd     : {res.cmd}\nok      : {res.ok}   compile {res.compile_s}s\n")
        if res.ok:
            s = res.static
            b.write(f"image   : text={s.get('text_b')} data={s.get('data_b')} bss={s.get('bss_b')} "
                    f"total={s.get('image_b')}  file={s.get('file_b')}\n")
            b.write(f"sections: .text={s.get('sec_text_b')} .rodata={s.get('sec_rodata_b')} "
                    f".eh_frame(+hdr)={s.get('sec_eh_b')} relocs={s.get('sec_reloc_b')}\n")
            b.write(f"stack   : worst frame {s.get('su_worst_frame_b')} B in {s.get('su_worst_fn')}, "
                    f"{s.get('su_dynamic_frames')} dynamic frames\n")
            b.write(f"largest : {', '.join(s.get('top_symbols', []))}\n")
            if res.warnings:
                b.write("warnings:\n" + textwrap.indent(res.warnings, "  ") + "\n")
        else:
            b.write("error:\n" + textwrap.indent(res.error, "  ") + "\n")
        b.write("\n")
        b.flush()

    def raw_run(self, rec):
        m = rec.get("metrics", {})
        tag = f"{self.current_tag}:{rec.get('tag', '')}"
        self.raw.writerow([tag, rec.get("status"), rec.get("source"), rec.get("maxrss_kb"),
                           rec.get("minflt"), rec.get("majflt"),
                           rec.get("elapsed_s"), rec.get("user_s"), rec.get("sys_s"), rec.get("vcsw"),
                           rec.get("ivcsw"), m.get("heap_peak_bytes"), m.get("vm_stk_kb"), m.get("rss_anon_kb"),
                           m.get("rss_file_kb"), m.get("checksum"), rec.get("cmd")])
        for ph in rec.get("phases", []):
            self.ph.writerow([tag, ph.get("name"), ph.get("vmrss_kb"), ph.get("vmhwm_kb"), ph.get("heap_cur"),
                              ph.get("heap_peak"), ph.get("t_s")])
        self.raw_f.flush()
        self.ph_f.flush()

    # -------------------------------------------------------------- header
    def header(self, env, cfg, floor):
        bar = "=" * WIDTH
        self.out(self.c(bar, "head"))
        self.out(self.c("CRITTER MEMORY LAB  --  What are the biggest impacts to memory usage?", "bold"))
        self.out(self.c(bar, "head"))
        rows = [("Host", f"{env['model']}  ({env['machine']}, {env['cpus']} CPUs, "
                         f"{env.get('mem_total_kb', 0) // 1024:,} MB RAM)"),
                ("OS / kernel", f"{env['os']}  /  {env['kernel']}"),
                ("Page size", f"{env['page_bytes']:,} bytes  (RSS is counted in whole pages)"),
                ("Compiler", env["cc_version"]), ("C library", env["libc"]),
                ("Measurement", f"{env['gnu_time']} -v  ({env.get('gnu_time_version', '')})" if env["gnu_time"]
                 else "tools/ctime (same rusage fields; GNU time not installed)"),
                ("CPU governor", env["governor"]), ("ASLR", f"{env['aslr']}  (setarch -R: {cfg['no_aslr']})"),
                ("Repeats", f"{cfg['repeats']} per configuration (median reported)"),
                ("Data volume", f"small N={cfg['n_small']:,} (code-dominated), large N={cfg['n_large']:,} "
                                f"(data-dominated)"),
                ("Process floor", f"{fmt_num(floor, 'KB')} max RSS for an empty main() at -O2"),
                ("Logs", self.dir)]
        for k, v in rows:
            self.out(f"  {k:<14}: {v}")
        for w in env["warnings"]:
            self.wrap(self.c("WARNING", "SKIP"), w, indent=13)
        self.out()

    def suite_banner(self, name, title, count):
        self.out()
        self.out(self.c("#" * WIDTH, "head"))
        self.out(self.c(f"# SUITE: {name.upper()}  --  {title}  ({count} tests)", "bold"))
        self.out(self.c("#" * WIDTH, "head"))

    def progress(self, msg):
        if not sys.stdout.isatty():
            return
        sys.stdout.write(f"\r  ... {msg[:WIDTH - 8]:<{WIDTH - 8}}\r")
        sys.stdout.flush()

    def clear_progress(self):
        if not sys.stdout.isatty():
            return
        sys.stdout.write("\r" + " " * WIDTH + "\r")
        sys.stdout.flush()

    # -------------------------------------------------------------- tests
    def test_head(self, t):
        self.clear_progress()
        self.out("-" * WIDTH)
        self.out(self.c(f"[{t.tid}] {t.title}", "bold") + f"    (suite: {t.suite})")
        self.wrap("TEST", t.what)
        self.wrap("TESTING", t.testing)
        if t.expect:
            self.out(f"  {'HYPOTHESIS':<10}: {t.expect}")

    def compare_block(self, oc):
        t = oc.test
        self.test_head(t)
        if oc.status != "done":
            self.out(f"  {'OUTCOME':<10}: " + self.c(f"SKIPPED -- {oc.reason}", "SKIP"))
            self.outcomes.append(oc)
            return
        self.out(f"  {'BASELINE':<10}: {t.baseline.label:<28} {t.baseline.describe()}")
        self.out(f"  {'VARIANT':<10}: {t.variant.label:<28} {t.variant.describe()}")
        self.out(f"  {'RESULTS':<10}: {'metric':<24}{'baseline':>14}{'variant':>14}   {'delta':<24}verdict")
        for d in oc.dims.values():
            thr = f" (+/-{fmt_num(d.thr, d.unit)})" if d.key == "rss" else ""
            self.out(f"{'':13}{d.label:<24}{fmt_num(d.base, d.unit):>14}{fmt_num(d.var, d.unit):>14}   "
                     f"{fmt_delta(d):<24}{self.verdict(d.verdict)}{thr}")
        fb, fv = oc.info["file"]
        tb, tv = oc.info["time"]
        mb, mv = oc.info["minflt"]
        self.out(f"{'':13}{'file on disk (info)':<24}{fmt_num(fb, 'B'):>14}{fmt_num(fv, 'B'):>14}")
        self.out(f"{'':13}{'minor faults (info)':<24}{fmt_num(mb, ''):>14}{fmt_num(mv, ''):>14}")
        self.out(f"{'':13}{'run time (info)':<24}{fmt_num(tb, 's'):>14}{fmt_num(tv, 's'):>14}")
        hyp = ""
        if oc.hypothesis != "n/a":
            hyp = f"   hypothesis {t.expect} -> " + self.c(oc.hypothesis, "PASS" if oc.hypothesis == "CONFIRMED" else "SKIP")
        cs = {True: "identical", False: self.c("CHANGED", "FAIL"), None: "n/a (different algorithm/type)"}[oc.checksum_match]
        self.out(f"  {'OUTCOME':<10}: " + self.verdict(oc.overall) + hyp + f"   output: {cs}")
        self.wrap("MEANING", oc.meaning)
        self.outcomes.append(oc)

    def scaling_block(self, oc):
        self.test_head(oc.test)
        ns = oc.extra["ns"]
        self.out(f"  {'RESULTS':<10}: max RSS by N")
        self.out(f"{'':13}{'configuration':<22}" + "".join(f"{n:>12,}" for n in ns))
        for label, row in oc.extra["table"].items():
            self.out(f"{'':13}{label:<22}" + "".join(f"{fmt_num(v, 'KB') if v else 'FAIL':>12}" for v in row))
        self.out(f"  {'OUTCOME':<10}:")
        for label, v in oc.extra["fits"].items():
            self.out(f"{'':13}{label:<22}{v['verdict']}")
        self.wrap("MEANING", oc.meaning)
        self.outcomes.append(oc)

    def limit_block(self, oc):
        self.test_head(oc.test)
        self.out(f"  {'RESULTS':<10}: {'configuration':<34}{'result':<38}{'max RSS':>12}")
        for row in oc.extra["rows"]:
            word = "PASS" if row["status"] == "ok" else "FAIL"
            res = self.c(word, word) + ("" if word == "PASS" else f" ({row['status']})")
            pad = 38 + (len(res) - len(_ANSI_RE.sub("", res)))
            self.out(f"{'':13}{row['label']:<34}{res:<{pad}}{fmt_num(row['rss'], 'KB') if row['rss'] else '-':>12}")
        self.wrap("OUTCOME", oc.overall)
        self.wrap("MEANING", oc.meaning)
        self.outcomes.append(oc)

    def staged_block(self, oc):
        self.test_head(oc.test)
        if oc.status != "done":
            self.out(f"  {'OUTCOME':<10}: " + self.c(f"SKIPPED -- {oc.reason}", "SKIP"))
            self.outcomes.append(oc)
            return
        for label, kb in oc.extra["stages"]:
            self.out(f"{'':13}{label:<40}{fmt_num(kb, 'KB'):>14}")
        d = oc.dims["rss"]
        self.out(f"{'':13}{'peak of staged processes':<40}{fmt_num(d.var, 'KB'):>14}")
        self.out(f"{'':13}{'single-process baseline':<40}{fmt_num(d.base, 'KB'):>14}   {fmt_delta(d)}")
        hyp = f"   hypothesis {oc.test.expect} -> {oc.hypothesis}"
        cs = "identical" if oc.checksum_match else self.c("CHANGED", "FAIL")
        self.out(f"  {'OUTCOME':<10}: " + self.verdict(oc.overall) + hyp + f"   output: {cs}")
        self.wrap("MEANING", oc.meaning)
        self.outcomes.append(oc)

    # -------------------------------------------------------------- summary
    def final_summary(self, env, cfg, floor, t_start):
        cmp_ = [o for o in self.outcomes if o.status == "done" and o.test.kind in ("compare", "staged")]
        self.out()
        self.out(self.c("=" * WIDTH, "head"))
        self.out(self.c("SUMMARY  --  which optimisations reduce, increase, or are neutral to memory", "bold"))
        self.out(self.c("=" * WIDTH, "head"))
        for word in (REDUCES, INCREASES, NEUTRAL):
            group = [o for o in cmp_ if o.overall_word == word]
            self.out(self.c(f"{word} ({len(group)})", word))
            for o in sorted(group, key=lambda o: lead_dim(o).pct):
                d = lead_dim(o)
                q = o.overall[len(word):].strip()
                self.out(f"   {o.test.tid:<12}{o.test.title[:52]:<54}{d.key:<6}{fmt_delta(d):<26}{q}")
        skipped = [o for o in self.outcomes if o.status != "done"]
        if skipped:
            self.out(self.c(f"SKIPPED ({len(skipped)})", "SKIP"))
            for o in skipped:
                self.out(f"   {o.test.tid:<12}{o.test.title[:52]:<54}{o.reason[:30]}")

        self.out()
        self.out(self.c("BIGGEST IMPACTS (absolute change in max RSS)", "bold"))
        ranked = sorted(cmp_, key=lambda o: -abs(o.dims["rss"].delta))[:12]
        for i, o in enumerate(ranked, 1):
            d = o.dims["rss"]
            self.out(f"  {i:>2}. {o.test.tid:<12}{o.test.title[:50]:<52}{fmt_delta(d):<26}N={o.n:,}")

        self.out()
        self.out(self.c("LEVER SIZE BY CATEGORY (largest |delta max RSS| in each suite)", "bold"))
        levers = {}
        for o in cmp_:
            key = o.test.suite + (" (small N)" if o.test.regime == "small" else "")
            if key not in levers or abs(o.dims["rss"].delta) > abs(levers[key].dims["rss"].delta):
                levers[key] = o
        for k, o in sorted(levers.items(), key=lambda kv: -abs(kv[1].dims["rss"].delta)):
            d = o.dims["rss"]
            self.out(f"  {k:<22}{fmt_num(abs(d.delta), 'KB'):>12}  ({abs(d.pct):5.1f}% of baseline)   via {o.test.tid} {o.test.variant.label if o.test.variant else ''}")

        scal = [o for o in self.outcomes if o.test.kind == "scaling" and o.status == "done"]
        if scal:
            self.out()
            self.out(self.c("SCALING (memory cost per retained sample)", "bold"))
            for o in scal:
                for label, f in o.extra["fits"].items():
                    self.out(f"  {o.test.tid:<6}{label:<22}{f['verdict']}")
        lims = [o for o in self.outcomes if o.test.kind == "limit" and o.status == "done"]
        if lims:
            self.out()
            self.out(self.c("DEPLOYABILITY (hard limits)", "bold"))
            for o in lims:
                self.out(f"  {o.test.tid:<6}{o.test.title}")
                self.out(f"        {o.overall}")
        hyp = [o for o in cmp_ if o.hypothesis != "n/a"]
        conf = sum(1 for o in hyp if o.hypothesis == "CONFIRMED")
        self.out()
        self.out(f"  Hypotheses: {conf}/{len(hyp)} confirmed; refuted ones are listed in summary.md for discussion.")
        changed = [o.test.tid for o in cmp_ if o.checksum_match is False]
        if changed:
            self.out(f"  Output changed (not a free win): {', '.join(changed)}")
        conclusion = self.conclusion(cmp_, levers)
        self.out()
        self.wrap("ANSWER", conclusion, indent=13)
        self.out()
        self.out(f"  Finished in {time.time() - t_start:,.0f} s.  Logs: {self.dir}")
        self.write_files(env, cfg, floor, cmp_, ranked, levers, conclusion)

    def conclusion(self, cmp_, levers):
        if not cmp_:
            return "No comparisons completed."
        top = max(cmp_, key=lambda o: abs(o.dims["rss"].delta))
        flag_small = [o for o in cmp_ if o.test.suite == "flags" and o.test.regime == "small"
                      and "sanitize" not in o.test.title]
        flag_large = [o for o in cmp_ if o.test.suite == "flags" and o.test.regime == "large"]
        design = [o for o in cmp_ if o.test.suite in ("data", "alloc", "algo", "overlay")]
        s = [f"The largest single impact was {top.test.tid} ({top.test.title}): "
             f"{fmt_delta(top.dims['rss'])} in max RSS."]
        if flag_small:
            mf = max(flag_small, key=lambda o: abs(o.dims["rss"].delta))
            s.append(f"Shipping-relevant compiler/linker flags moved max RSS by at most "
                     f"{fmt_num(abs(mf.dims['rss'].delta), 'KB')} ({mf.test.variant.label}) at small N.")
        if flag_large:
            mf = max(flag_large, key=lambda o: abs(o.dims["rss"].delta))
            s.append(f"At production volume the biggest flag effect was {fmt_num(abs(mf.dims['rss'].delta), 'KB')} "
                     f"({abs(mf.dims['rss'].pct):.1f}%).")
        if design:
            md = max(design, key=lambda o: abs(o.dims["rss"].delta))
            s.append(f"Design choices (representation, buffering, algorithm, phase lifetime) moved it by up to "
                     f"{fmt_num(abs(md.dims['rss'].delta), 'KB')} ({abs(md.dims['rss'].pct):.0f}%, {md.test.tid}).")
        s.append("Flags shape the image and the stack; data structures and buffer lifetimes decide resident memory.")
        return " ".join(s)

    # -------------------------------------------------------------- files
    def write_files(self, env, cfg, floor, cmp_, ranked, levers, conclusion):
        fields = ["tid", "suite", "unit", "title", "kind", "regime", "n", "status", "reason",
                  "baseline", "baseline_config", "variant", "variant_config",
                  "rss_base_kb", "rss_var_kb", "rss_delta_kb", "rss_pct", "rss_threshold_kb", "rss_verdict",
                  "image_base_b", "image_var_b", "image_delta_b", "image_verdict",
                  "heap_base_b", "heap_var_b", "heap_verdict", "stack_base_b", "stack_var_b", "stack_verdict",
                  "file_base_b", "file_var_b", "minflt_base", "minflt_var", "time_base_s", "time_var_s",
                  "overall", "expect", "hypothesis", "checksum_match", "tradeoffs", "what", "testing", "meaning"]
        rows, jrows = [], []
        for o in self.outcomes:
            t = o.test
            r = {"tid": t.tid, "suite": t.suite, "unit": t.unit, "title": t.title, "kind": t.kind,
                 "regime": t.regime, "n": o.n, "status": o.status, "reason": o.reason,
                 "baseline": t.baseline.label if t.baseline else "", "baseline_config": t.baseline.describe() if t.baseline else "",
                 "variant": t.variant.label if t.variant else "", "variant_config": t.variant.describe() if t.variant else "",
                 "overall": o.overall, "expect": t.expect, "hypothesis": o.hypothesis,
                 "checksum_match": o.checksum_match, "tradeoffs": "; ".join(o.tradeoffs),
                 "what": t.what, "testing": t.testing, "meaning": o.meaning}
            for key, d in o.dims.items():
                if key == "rss":
                    r.update(rss_base_kb=d.base, rss_var_kb=d.var, rss_delta_kb=d.delta, rss_pct=round(d.pct, 2),
                             rss_threshold_kb=round(d.thr, 1), rss_verdict=d.verdict)
                else:
                    r[f"{key}_base_b"], r[f"{key}_var_b"], r[f"{key}_verdict"] = d.base, d.var, d.verdict
                    if key == "image":
                        r["image_delta_b"] = d.delta
            if o.info:
                r["file_base_b"], r["file_var_b"] = o.info.get("file", (None, None))
                r["minflt_base"], r["minflt_var"] = o.info.get("minflt", (None, None))
                r["time_base_s"], r["time_var_s"] = o.info.get("time", (None, None))
            rows.append(r)
            j = dict(r)
            j["extra"] = o.extra
            if o.var_meas:
                j["variant_phases"] = o.var_meas.get("phases")
            if o.base_meas:
                j["baseline_phases"] = o.base_meas.get("phases")
            jrows.append(j)
        with open(os.path.join(self.dir, "results.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(self.dir, "results.json"), "w") as f:
            json.dump({"environment": env, "config": cfg, "process_floor_kb": floor, "results": jrows,
                       "conclusion": conclusion}, f, indent=1, default=str)
        self.write_markdown(env, cfg, floor, cmp_, ranked, levers, conclusion)
        for fh in (self.console, self.builds, self.raw_f, self.ph_f):
            fh.flush()

    def write_markdown(self, env, cfg, floor, cmp_, ranked, levers, conclusion):
        L = []
        L.append("# Critter Memory Lab -- results summary\n")
        L.append("**Question:** What are the biggest impacts to memory usage?\n")
        L.append(f"**Answer (auto-generated from the data):** {conclusion}\n")
        L.append("## Test environment\n")
        L.append("| item | value |\n|---|---|")
        for k, v in [("host", f"{env['model']} ({env['machine']})"), ("OS / kernel", f"{env['os']} / {env['kernel']}"),
                     ("page size", f"{env['page_bytes']} B"), ("compiler", env["cc_version"]), ("libc", env["libc"]),
                     ("measurement", "GNU time -v" if env["gnu_time"] else "tools/ctime stand-in (GNU time missing)"),
                     ("repeats", cfg["repeats"]), ("small / large N", f"{cfg['n_small']:,} / {cfg['n_large']:,}"),
                     ("process floor", fmt_num(floor, "KB"))]:
            L.append(f"| {k} | {v} |")
        L.append("\n**Classification rule.** A change counts only if it exceeds the noise threshold: max RSS "
                 "needs max(2 pages, 2x run-to-run spread, 0.5%); image/heap/stack sizes are deterministic and "
                 "use 0.5%/0.5%/2%. Overall verdict = resident verdict if it moved, else stack, else image.\n")
        for word in (REDUCES, INCREASES, NEUTRAL):
            group = [o for o in cmp_ if o.overall_word == word]
            L.append(f"## {word} memory ({len(group)})\n")
            if not group:
                L.append("_none_\n")
                continue
            L.append("| test | change | max RSS delta | image delta | stack delta | hypothesis |\n|---|---|---|---|---|---|")
            for o in sorted(group, key=lambda o: lead_dim(o).pct):
                im, st = o.dims.get("image"), o.dims.get("stack")
                L.append(f"| {o.test.tid} | {o.test.title} | {fmt_delta(o.dims['rss'])} | "
                         f"{fmt_delta(im) if im else '-'} | {fmt_delta(st) if st else '-'} | {o.hypothesis} |")
            L.append("")
        L.append("## Biggest impacts\n\n| rank | test | change | max RSS delta | N |\n|---|---|---|---|---|")
        for i, o in enumerate(ranked, 1):
            L.append(f"| {i} | {o.test.tid} | {o.test.title} | {fmt_delta(o.dims['rss'])} | {o.n:,} |")
        L.append("\n## Lever size by category\n\n| category | largest effect | % of baseline | via |\n|---|---|---|---|")
        for k, o in sorted(levers.items(), key=lambda kv: -abs(kv[1].dims["rss"].delta)):
            d = o.dims["rss"]
            L.append(f"| {k} | {fmt_num(abs(d.delta), 'KB')} | {abs(d.pct):.1f}% | {o.test.tid} {o.test.variant.label if o.test.variant else ''} |")
        for o in self.outcomes:
            if o.test.kind == "scaling":
                L.append(f"\n## {o.test.tid} {o.test.title}\n")
                L.append("| configuration | " + " | ".join(f"N={n:,}" for n in o.extra["ns"]) + " | verdict |")
                L.append("|---|" + "---|" * (len(o.extra["ns"]) + 1))
                for label, row in o.extra["table"].items():
                    L.append(f"| {label} | " + " | ".join(fmt_num(v, 'KB') if v else "FAIL" for v in row) +
                             f" | {o.extra['fits'][label]['verdict']} |")
            elif o.test.kind == "limit":
                L.append(f"\n## {o.test.tid} {o.test.title}\n\n| configuration | result | max RSS |\n|---|---|---|")
                for row in o.extra["rows"]:
                    L.append(f"| {row['label']} | {'PASS' if row['status'] == 'ok' else 'FAIL: ' + row['status']} | "
                             f"{fmt_num(row['rss'], 'KB') if row['rss'] else '-'} |")
                L.append(f"\n{o.meaning}")
        refuted = [o for o in cmp_ if o.hypothesis == "REFUTED"]
        if refuted:
            L.append("\n## Refuted hypotheses (discussion material)\n")
            for o in refuted:
                L.append(f"- **{o.test.tid} {o.test.title}**: expected {o.test.expect}, observed {o.overall}.")
        L.append("\n## Per-test write-ups\n")
        for o in self.outcomes:
            t = o.test
            L.append(f"### {t.tid} -- {t.title}\n")
            L.append(f"- **Test:** {t.what}\n- **Testing:** {t.testing}")
            if t.expect:
                L.append(f"- **Hypothesis:** {t.expect}")
            if o.status != "done":
                L.append(f"- **Outcome:** SKIPPED ({o.reason})\n")
                continue
            if t.kind in ("compare", "staged"):
                dims = "; ".join(f"{d.label}: {fmt_num(d.base, d.unit)} -> {fmt_num(d.var, d.unit)} "
                                 f"({fmt_delta(d)}, {d.verdict})" for d in o.dims.values())
                L.append(f"- **Outcome:** {o.overall} -- {dims}")
            else:
                L.append(f"- **Outcome:** {o.overall}")
            L.append(f"- **Meaning:** {o.meaning}\n")
        with open(os.path.join(self.dir, "summary.md"), "w") as f:
            f.write("\n".join(L) + "\n")
