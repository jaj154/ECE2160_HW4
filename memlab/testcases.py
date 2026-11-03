"""Every experiment in the lab, declared as data.

Each TestCase states, before anything runs:
  what      the procedure (what is built and run)
  testing   the question / mechanism under test
  expect    the hypothesis (REDUCES / INCREASES / NEUTRAL)
  insight   the mechanism, used to explain the outcome
so the printed result can say whether the hypothesis held.

To add an experiment, append a TestCase in the relevant suite function.
"""
import platform
from dataclasses import dataclass, field, replace

from .build import BuildSpec

# The "junior-developer prototype" configuration of each unit: this is the
# baseline every optimisation is measured against.
UNIT_DEFAULT_ARGS = {
    "noop": {},
    "io": {"strategy": "grow", "window": 1000},
    "mem": {"strategy": "copy_sort", "window": 1000},
    "compute": {"mode": "materialized", "scratch": "heap", "p": 8, "horizon": 4000, "depth": 10},
    "pipeline": {"mode": "concurrent", "fit": "materialized", "p": 8},
}
UNIT_ROLE = {
    "noop": "empty program (process floor)",
    "io": "I/O unit (high-rate acquisition)",
    "mem": "memory unit (outlier removal + summaries)",
    "compute": "compute unit (HVAC prediction)",
    "pipeline": "full Critter pipeline",
}


@dataclass(frozen=True)
class Variant:
    label: str
    unit: str
    cflags: tuple = ("-O2",)
    ldflags: tuple = ()
    defines: tuple = ()
    args: tuple = ()       # overrides of UNIT_DEFAULT_ARGS: (("strategy","ring"),)
    env: tuple = ()
    rlimits: tuple = ()    # (("AS", bytes),) or (("STACK", bytes),)

    def spec(self, probe=False):
        return BuildSpec(self.unit, tuple(self.cflags), tuple(self.ldflags), tuple(self.defines), probe)

    def argv(self, n):
        a = dict(UNIT_DEFAULT_ARGS[self.unit])
        a.update(dict(self.args))
        if self.unit != "noop":
            a["n"] = n
        return tuple(f"--{k}={v}" for k, v in a.items())

    def describe(self):
        bits = [" ".join(self.cflags + self.ldflags)]
        if self.defines:
            bits.append(" ".join(f"-D{k}={v}" for k, v in self.defines))
        if self.args:
            bits.append(" ".join(f"--{k}={v}" for k, v in self.args))
        if self.env:
            bits.append(" ".join(f"{k}={v}" for k, v in self.env))
        if self.rlimits:
            bits.append(" ".join(f"rlimit_{k}={v // 1024}KB" for k, v in self.rlimits))
        return "  ".join(b for b in bits if b)


@dataclass
class TestCase:
    tid: str
    suite: str
    title: str
    unit: str
    what: str
    testing: str
    kind: str = "compare"            # compare | scaling | limit | staged
    baseline: Variant = None
    variant: Variant = None
    variants: list = field(default_factory=list)
    expect: str = "NEUTRAL"
    insight: str = ""
    regime: str = "large"            # small (code-dominated) | large (data-dominated)
    measure_stack: bool = False
    same_output: bool = True         # checksum must match baseline
    n_override: int = 0
    note: str = ""


def _flag_variant(unit, label, cflags, ldflags=(), base=("-O2",)):
    cf = tuple(cflags) if cflags and cflags[0].startswith("-O") and len(cflags[0]) <= 3 else base + tuple(cflags)
    return Variant(label=label, unit=unit, cflags=cf, ldflags=tuple(ldflags))


def native_cpu_flag():
    m = platform.machine()
    if m in ("aarch64", "arm64"):
        return "-mcpu=native"   # cortex-a76 on a Pi 5
    return "-march=native"


# --------------------------------------------------------------------------- #
# (flag(s), linker flags, hypothesis, mechanism)
# A leading -Ox replaces -O2 (group comparison for context); every other entry
# is ADDED to -O2 so exactly one optimisation changes per test.
FLAG_MATRIX = [
    (["-O0"], [], "INCREASES",
     "No register allocation: every local lives in a stack slot, nothing is inlined and tail calls "
     "are not eliminated, so frames and code both grow."),
    (["-O1"], [], "NEUTRAL",
     "-O1 drops the inlining heuristics and IPA passes of -O2, so code is similar in size and data are "
     "untouched. Watch the stack: -foptimize-sibling-calls is an -O2 pass, so tail recursion is NOT "
     "removed at -O1."),
    (["-O3"], [], "INCREASES",
     "-O3 adds aggressive inlining, loop versioning, unswitching and vectorisation; each duplicates code."),
    (["-Os"], [], "REDUCES",
     "-Os is -O2 minus size-increasing passes (alignment padding, unrolling, most inlining)."),
    (["-Oz"], [], "REDUCES",
     "-Oz (GCC 12+) minimises size even at a speed cost (e.g. no function alignment, call-heavy code)."),
    (["-Og"], [], "INCREASES",
     "-Og keeps variables observable for the debugger and, like -O1, leaves tail calls as real calls."),
    (["-funroll-loops"], [], "INCREASES",
     "Unrolling replicates loop bodies to cut branch overhead: a pure code-for-speed trade."),
    (["-funroll-all-loops"], [], "INCREASES",
     "Unrolls even loops with unknown trip counts, adding remainder loops as well."),
    (["-finline-limit=1000"], [], "INCREASES",
     "Raises the inlining budget, so callee bodies are copied into every call site."),
    (["-fno-inline"], [], "REDUCES",
     "Disables inlining: calls replace copies. Note the catch: small static inline helpers (s_to_c, "
     "c_to_s) then become out-of-line copies in every translation unit, so code can even grow."),
    (["-ftree-vectorize", "-fvect-cost-model=dynamic"], [], "INCREASES",
     "O3-style vectorisation: SIMD body plus scalar prologue/epilogue and runtime alias checks."),
    (["-fipa-cp-clone"], [], "INCREASES",
     "Clones functions specialised for constant arguments, trading code size for speed."),
    (["-ffunction-sections", "-fdata-sections"], ["-Wl,--gc-sections"], "REDUCES",
     "Each function/object in its own section lets the linker discard unreferenced ones."),
    (["-flto"], [], "REDUCES",
     "Link-time optimisation sees the whole program: removes dead code and specialises across units."),
    (["-fno-asynchronous-unwind-tables", "-fno-unwind-tables"], [], "REDUCES",
     "Drops .eh_frame unwind tables; C code without exceptions does not need them to run."),
    (["-fmerge-all-constants"], [], "NEUTRAL",
     "Merges identical constants and arrays across the program; few duplicates exist here."),
    (["-fshort-enums"], [], "NEUTRAL",
     "Enums take the smallest integer type; no bulk data here is enum-typed."),
    (["-fno-plt"], [], "NEUTRAL",
     "Calls shared-library functions through the GOT instead of PLT stubs; tiny, mixed effect."),
    (["-fno-pie"], ["-no-pie"], "REDUCES",
     "Position-dependent executables need fewer dynamic relocations and GOT entries."),
    ([], ["-static"], "REDUCES",
     "Static linking pulls libc into the image (image grows) but avoids mapping the shared libc, "
     "the loader and relocation of a single process (resident shrinks). Shared libraries only pay off "
     "when many processes share them."),
    ([], ["-s"], "NEUTRAL",
     "Strips the symbol table: smaller file on disk, but symbols are never loaded, so RAM is unchanged."),
    (["-g"], [], "NEUTRAL",
     "Debug info lives in non-allocated sections: the file grows, the resident image does not."),
    (["-fstack-protector-all"], [], "INCREASES",
     "A canary slot and check sequence in every function: slightly larger frames and code."),
    (["-fstack-protector-strong"], [], "INCREASES",
     "Canaries only in functions with local arrays or address-taken locals."),
    (["-fstack-clash-protection"], [], "INCREASES",
     "Probes each page of large stack allocations; adds code only where frames are large."),
    (["-D_FORTIFY_SOURCE=2"], [], "NEUTRAL",
     "Bounds-checked variants of memcpy/strcpy etc. where sizes are known; a few extra bytes."),
    (["-fno-omit-frame-pointer"], [], "INCREASES",
     "Keeps a frame pointer: one register lost and a save/restore per frame."),
    (["-fomit-frame-pointer"], [], "NEUTRAL",
     "Already enabled at -O1 and above on these targets; included as a check that it is a no-op."),
    (["-fno-optimize-sibling-calls"], [], "INCREASES",
     "Disables tail-call elimination: the recursive forecast keeps one frame per step instead of "
     "becoming a loop."),
    ([native_cpu_flag()], [], "NEUTRAL",
     "Tunes instruction selection for this exact CPU; code size and data size barely change."),
    (["-ffast-math"], [], "NEUTRAL",
     "Relaxes IEEE rules; memory-neutral, but it may change numerical results (watch the checksum)."),
    (["-fvisibility=hidden"], [], "NEUTRAL",
     "Hides symbols from the dynamic table; executables export very little anyway."),
    (["-fPIC"], [], "NEUTRAL",
     "Library-style position independence in an executable: GOT-relative addressing, similar size."),
    (["-fno-common"], [], "NEUTRAL",
     "Default since GCC 10; included as a check that it is a no-op."),
    (["-pipe"], [], "NEUTRAL",
     "NEGATIVE CONTROL: -pipe only changes how the compiler passes temporary files. Any 'change' "
     "here is measurement noise, which validates the noise threshold."),
    (["-fsanitize=address"], [], "INCREASES",
     "AddressSanitizer: shadow memory (1/8 of address space reserved), redzones around every "
     "allocation and a quarantine of freed blocks. A debugging tool, never a shipping config."),
    # ---- follow-up flags (ids 37+), stack- and size-oriented ----
    (["-fconserve-stack"], [], "REDUCES",
     "Asks GCC to minimise stack use, mainly by refusing inlining that would grow a caller's frame."),
    (["-falign-functions=1"], [], "REDUCES",
     "Removes the padding GCC inserts so each function starts on a cache-line-friendly boundary."),
    (["-falign-loops=1"], [], "REDUCES",
     "Removes the padding inserted before loop heads."),
    (["-falign-functions=1", "-falign-jumps=1", "-falign-loops=1", "-falign-labels=1"], [], "REDUCES",
     "All code-alignment padding removed together."),
    (["-flto", "-fwhole-program"], [], "REDUCES",
     "LTO plus the promise that the program is complete: every function except main becomes local, "
     "so unused externally visible code can be discarded."),
    ([], ["-Wl,-z,norelro"], "REDUCES",
     "Drops the RELRO segment, which is page-aligned and made read-only after relocation; with 16 KB "
     "pages its alignment can cost a page."),
    ([], ["-Wl,-z,noseparate-code"], "REDUCES",
     "Lets the linker place code and read-only data in fewer page-aligned segments, removing padding "
     "that 16 KB pages make expensive."),
]


def suite_flags(cfg):
    tests = []
    units = [u for u in ("io", "mem", "compute") if u in cfg["flag_units"]]
    for unit in units:
        base = Variant("-O2 (baseline)", unit)
        for i, (cf, lf, expect, insight) in enumerate(FLAG_MATRIX, 1):
            label = " ".join(cf + lf)
            var = _flag_variant(unit, label, cf, lf)
            tid = f"F-{unit.upper()[:3]}-{i:02d}"
            tests.append(TestCase(
                tid=tid, suite="flags", title=f"{label}  [{unit}]", unit=unit,
                what=(f"Build the {UNIT_ROLE[unit]} at -O2 and again with '{label}'; run each "
                      f"{cfg['repeats']}x at N={cfg['n_small']:,} under time -v; read image sizes with size(1) "
                      f"and the stack high-water mark from a probe build."),
                testing=f"Does '{label}' change resident memory, image size or stack depth?",
                baseline=base, variant=var, expect=expect, insight=insight, regime="small",
                measure_stack=cfg["stack_probe"] and "sanitize" not in label,
                same_output="fast-math" not in label))
    # A few headline flags again at production data volume (data-dominated)
    data_dominated = ("Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even "
                      "a real code-size change is a rounding error in resident memory.")
    large = [
        (["-O0"], [], "NEUTRAL", data_dominated),
        (["-Os"], [], "NEUTRAL", data_dominated),
        (["-O3"], [], "NEUTRAL", data_dominated),
        (["-flto"], [], "NEUTRAL", data_dominated),
        ([], ["-static"], "REDUCES",
         "Static linking removes a FIXED cost (shared libc mapping, loader, relocations), so it saves "
         "about the same absolute amount at any N -- a shrinking percentage as data grow."),
    ]
    large_ids = {"mem": "F-LARGE", "io": "F-LIO", "compute": "F-LCOM"}
    for unit in ("mem", "io", "compute"):
        for i, (cf, lf, expect, insight) in enumerate(large, 1):
            label = " ".join(cf + lf)
            tests.append(TestCase(
                tid=f"{large_ids[unit]}-{i:02d}", suite="flags", title=f"{label} at production volume [{unit}]",
                unit=unit,
                what=(f"Same comparison as the small-N flag tests, but the {UNIT_ROLE[unit]} processes "
                      f"N={cfg['n_large']:,} samples (data-dominated regime)."),
                testing=f"Once data dominate the footprint, does '{label}' still matter?",
                baseline=Variant("-O2 (baseline)", unit), variant=_flag_variant(unit, label, cf, lf),
                expect=expect, regime="large", insight=insight))
    return tests


def suite_data(cfg):
    T = []
    D = lambda unit, label, defs: Variant(label, unit, defines=tuple(defs))
    T.append(TestCase("D-01", "data", "Sample type double -> float [io]", "io",
                      "Recompile the I/O unit with CRITTER_SAMPLE_TYPE=float; same N, same naive record layout.",
                      "How much of the acquisition buffer is the temperature representation?",
                      baseline=D("io", "double", []), variant=D("io", "float", [("CRITTER_SAMPLE_TYPE", 1)]),
                      expect="REDUCES", same_output=False,
                      insight="The naive record shrinks from 24 to 16 bytes; float still resolves 0.001 C."))
    T.append(TestCase("D-02", "data", "Sample type double -> fixed16 [io]", "io",
                      "Recompile the I/O unit with CRITTER_SAMPLE_TYPE=fixed16 (int16 centi-degrees C).",
                      "Can a fixed-point representation sized to the sensor's real resolution shrink the buffer?",
                      baseline=D("io", "double", []), variant=D("io", "fixed16", [("CRITTER_SAMPLE_TYPE", 2)]),
                      expect="REDUCES", same_output=False,
                      insight=("A machine-room sensor resolves ~0.01-0.1 C over -40..125 C: 2 bytes are enough. "
                               "The record drops to 12 bytes (half of the double version).")))
    T.append(TestCase("D-03", "data", "Record layout naive -> reordered [io]", "io",
                      "Recompile with CRITTER_LAYOUT=1: identical fields, ordered largest-alignment first.",
                      "How much memory is wasted in struct padding?",
                      baseline=D("io", "naive", []), variant=D("io", "reordered", [("CRITTER_LAYOUT", 1)]),
                      expect="REDUCES",
                      insight=("{u8, double, u8, u32} has 7+3 bytes of padding holes (24 B); "
                               "{double, u32, u8, u8} needs only 2 bytes of tail padding (16 B). Zero cost.")))
    T.append(TestCase("D-04", "data", "Record layout naive -> packed [io]", "io",
                      "Recompile with CRITTER_LAYOUT=2: __attribute__((packed)) on the naive order.",
                      "Does removing all padding beat reordering, and what does it cost?",
                      baseline=D("io", "naive", []), variant=D("io", "packed", [("CRITTER_LAYOUT", 2)]),
                      expect="REDUCES",
                      insight=("Packed records are 14 B (vs 16 B reordered) but force unaligned loads; on "
                               "Cortex-A76 these are legal but slower, and on Cortex-M0 they fault. "
                               "Reordering gets most of the gain for free.")))
    T.append(TestCase("D-05", "data", "Sample type double -> float [mem]", "mem",
                      "Recompile the memory unit (copy_sort) with float samples.",
                      "Does halving the element size halve the outlier-removal footprint?",
                      baseline=D("mem", "double", []), variant=D("mem", "float", [("CRITTER_SAMPLE_TYPE", 1)]),
                      expect="REDUCES", same_output=False,
                      insight=("Only 3 of the 4 N-sized buffers shrink: the junior-dev code always builds a "
                               "double deviation array. The type of the dominant buffer is what matters.")))
    T.append(TestCase("D-06", "data", "Sample type double -> fixed16 [mem]", "mem",
                      "Recompile the memory unit (copy_sort) with int16 fixed-point samples.",
                      "How far can representation alone go for the memory unit?",
                      baseline=D("mem", "double", []), variant=D("mem", "fixed16", [("CRITTER_SAMPLE_TYPE", 2)]),
                      expect="REDUCES", same_output=False,
                      insight="Raw, sorted and cleaned copies drop to 2 B/sample; the double deviation array stays 8 B."))
    T.append(TestCase("D-07", "data", "Input type double -> fixed16 [compute]", "compute",
                      "Recompile the compute unit (materialized fit) with int16 input samples.",
                      "Does shrinking the input help when the working set is a derived matrix?",
                      baseline=D("compute", "double", []), variant=D("compute", "fixed16", [("CRITTER_SAMPLE_TYPE", 2)]),
                      expect="REDUCES", same_output=False,
                      insight=("The design matrix X and its transpose are 2 x N x p doubles (128 B/sample at p=8); "
                               "the input is 8 B/sample. Shrinking the input barely dents the total: optimise "
                               "the dominant buffer first.")))
    return T


def suite_alloc(cfg):
    n = cfg["n_large"]
    IO = lambda label, **a: Variant(label, "io", args=tuple(a.items()))
    return [
        TestCase("A-01", "alloc", "Growable vector -> exact heap allocation [io]", "io",
                 "Run the I/O unit with --strategy=heap (one malloc of N records) instead of realloc doubling.",
                 "What does not knowing the size in advance cost?",
                 baseline=IO("grow"), variant=IO("heap", strategy="heap"), expect="REDUCES",
                 insight=("Doubling rounds capacity up to the next power of two and realloc may briefly hold "
                          "old and new blocks. Compare tracked heap (bytes reserved) with max RSS (pages "
                          "touched): on Linux the unused tail of a large mmap'd block is never touched, and "
                          "glibc grows big blocks with mremap instead of copying, so the waste is address "
                          "space, not RAM. On an MCU heap the same tail is real, unusable RAM.")),
        TestCase("A-02", "alloc", "Growable vector -> static .bss buffer [io]", "io",
                 f"Rebuild with -DCRITTER_IO_STATIC_CAP={n} and run --strategy=static.",
                 "Heap vs. statically reserved buffer: resident cost and image cost.",
                 baseline=IO("grow"),
                 variant=Variant("static", "io", defines=(("CRITTER_IO_STATIC_CAP", n),), args=(("strategy", "static"),)),
                 expect="REDUCES",
                 insight=("Resident cost equals the exact-heap case (pages are touched the same way) but the "
                          "buffer moves into .bss: the image grows by N x record size. On an MCU that is RAM "
                          "reserved at link time, which is exactly what makes worst-case usage provable.")),
        TestCase("A-03", "alloc", "Store-everything -> bounded ring buffer [io]", "io",
                 "Run the I/O unit with --strategy=ring: keep only the current W=1000-record window.",
                 "Does the I/O unit need to retain the raw stream at all?",
                 baseline=IO("grow"), variant=IO("ring", strategy="ring"), expect="REDUCES",
                 insight=("Summaries are computed as each window fills, so memory is O(W) instead of O(N) and "
                          "the output is bit-identical. This is the single most important embedded pattern: "
                          "bounded buffers make memory independent of uptime.")),
        TestCase("A-04", "alloc", "Allocator policy: mmap threshold raised [pipeline/phased]", "pipeline",
                 "Run the phased pipeline with GLIBC_TUNABLES=glibc.malloc.mmap_threshold=33554432 so that "
                 "blocks up to 32 MB come from the brk heap instead of mmap.",
                 "Does freeing memory actually give it back to the OS?",
                 baseline=Variant("default malloc", "pipeline", args=(("mode", "phased"),)),
                 variant=Variant("mmap_threshold=32MB", "pipeline", args=(("mode", "phased"),),
                                 env=(("GLIBC_TUNABLES", "glibc.malloc.mmap_threshold=33554432"),)),
                 expect="INCREASES",
                 insight=("mmap'd blocks are unmapped on free(); brk-heap blocks are only returned if they sit "
                          "at the top of the heap. 'Phased' code relies on free() releasing memory, so the "
                          "allocator policy decides whether phasing works.")),
    ]


def suite_algo(cfg):
    M = lambda label, s: Variant(label, "mem", args=(("strategy", s),))
    C = lambda label, m: Variant(label, "compute", args=(("mode", m),))
    return [
        TestCase("G-01", "algo", "copy+qsort -> quickselect in place [mem]", "mem",
                 "Run the memory unit with --strategy=inplace (one scratch copy, quickselect, in-place compaction).",
                 "How much of the junior-dev footprint is avoidable copying?",
                 baseline=M("copy_sort", "copy_sort"), variant=M("inplace", "inplace"), expect="REDUCES",
                 insight=("Four N-sized buffers become two, and the scratch is freed before summarising. Results are "
                          "identical. Also compare RSS with tracked heap: glibc's qsort may malloc a hidden "
                          "temporary the size of the array (merge sort), memory the program never asked for.")),
        TestCase("G-02", "algo", "copy+qsort -> fixed histogram [mem]", "mem",
                 "Run --strategy=histogram: median and MAD from a 20001-bin (80 KB) histogram, no copy.",
                 "Can sensor-domain knowledge replace a data-sized buffer with a fixed one?",
                 baseline=M("copy_sort", "copy_sort"), variant=M("histogram", "histogram"), expect="REDUCES",
                 same_output=False,
                 insight=("The sensor's range and resolution are known, so a counting histogram gives the median "
                          "in O(1) extra memory (quantised to 0.01 C, which is the sensor's resolution anyway).")),
        TestCase("G-03", "algo", "batch -> streaming windows [mem]", "mem",
                 "Run --strategy=streaming: robust filtering per W=1000 window; the full stream is never stored.",
                 "What is the floor for the memory unit if data are processed as they arrive?",
                 baseline=M("copy_sort", "copy_sort"), variant=M("streaming", "streaming"), expect="REDUCES",
                 same_output=False,
                 insight=("Memory is O(W), independent of N. The statistic becomes local (per-window median), "
                          "which tracks HVAC drift better but is a design decision, not a free optimisation.")),
        TestCase("G-04", "algo", "materialized matrix -> streaming normal equations [compute]", "compute",
                 "Run the compute unit with --mode=streaming: accumulate XtX and Xty sample by sample.",
                 "Does the prediction need the design matrix at all?",
                 baseline=C("materialized", "materialized"), variant=C("streaming", "streaming"), expect="REDUCES",
                 insight=("Least squares only needs XtX (p x p) and Xty (p). Materialising X and an explicit "
                          "transpose costs 2 x N x p doubles; streaming costs p^2 doubles. Identical coefficients.")),
    ]


def suite_overlay(cfg):
    P = lambda label, mode, fit="materialized": Variant(label, "pipeline", args=(("mode", mode), ("fit", fit)))
    conc = P("concurrent", "concurrent")
    return [
        TestCase("O-01", "overlay", "All buffers live -> free when dead (phased)", "pipeline",
                 "Run the full pipeline with --mode=phased: each phase frees its buffers before the next starts.",
                 "Is peak memory the sum of the phases or the maximum phase?",
                 baseline=conc, variant=P("phased", "phased"), expect="REDUCES",
                 insight=("Concurrent peak = SUM of all buffers; phased peak = MAX over phases. The saving is "
                          "bounded by the phases that are not the largest one.")),
        TestCase("O-02", "overlay", "All buffers live -> data overlay arena", "pipeline",
                 "Run --mode=overlay: one arena sized for the largest phase; cleaned data overlay the raw data "
                 "and the design matrix overlays the cleaning scratch.",
                 "Does a classic overlay scheme (applied to data) reduce peak memory?",
                 baseline=conc, variant=P("overlay", "overlay"), expect="REDUCES",
                 insight=("An overlay plan fixes the peak at compile/plan time: raw + max(scratch, design matrix). "
                          "No allocator, no fragmentation, and the worst case is known before deployment.")),
        TestCase("O-03", "overlay", "Phased (allocator) -> overlay (planned)", "pipeline",
                 "Compare --mode=phased with --mode=overlay directly.",
                 "Is there any resident difference between letting malloc reuse memory and planning reuse?",
                 baseline=P("phased", "phased"), variant=P("overlay", "overlay"), expect="NEUTRAL",
                 insight=("Both reach peak = largest phase. The overlay's value is determinism (no heap churn, "
                          "no fragmentation over months of uptime), not a smaller peak.")),
        TestCase("O-04", "overlay", "Overlay + streaming fit (shrink the dominant phase)", "pipeline",
                 "Run --mode=overlay --fit=streaming against the concurrent junior-dev pipeline.",
                 "Combine the overlay with removing the largest phase's buffers.",
                 baseline=conc, variant=P("overlay+streaming", "overlay", "streaming"), expect="REDUCES",
                 insight=("Overlays can only reduce peak to the largest phase; to go lower you must shrink that "
                          "phase. With the design matrix gone the peak falls to raw + scratch.")),
        TestCase("O-05", "overlay", "Single process -> one process per phase (exec overlay)", "pipeline",
                 "Run acquire, clean and predict as three separate processes that hand data off through a "
                 "file; peak = the largest of the three max RSS values.",
                 "Does splitting the pipeline into processes (the OS version of an overlay) lower the peak?",
                 kind="staged", baseline=conc, expect="REDUCES",
                 insight=("Each process starts with an empty heap and returns everything at exit, so peak is "
                          "the largest stage; the cost is file I/O and one process floor per stage.")),
    ]


def suite_stack(cfg):
    n = cfg["n_small"]
    C = lambda label, cf=("-O2",), **a: Variant(label, "compute", cflags=tuple(cf), args=tuple(a.items()))
    lim = cfg["stack_limit_kb"] * 1024
    return [
        TestCase("S-01", "stack", "Solver workspace heap -> stack [compute]", "compute",
                 "Run the compute unit with --scratch=stack: the 8 KB system + 32 KB trajectory become locals.",
                 "Where does moving a buffer from heap to stack show up?",
                 baseline=C("scratch=heap"), variant=C("scratch=stack", scratch="stack"), expect="INCREASES",
                 measure_stack=True, regime="small",
                 insight=("The bytes merely move: heap shrinks, stack grows by ~40 KB. With an 8 MB default stack "
                          "this is invisible on Linux; on an RTOS task with a 4 KB stack it is a crash.")),
        TestCase("S-02", "stack", "Solver workspace heap -> static [compute]", "compute",
                 "Run with --scratch=static: the workspace is a .bss array.",
                 "Static allocation: what moves to the image, what leaves the heap?",
                 baseline=C("scratch=heap"), variant=C("scratch=static", scratch="static"), expect="NEUTRAL",
                 measure_stack=True, regime="small",
                 insight=("The .bss array is in every compute build, so resident memory is the same; static "
                          "placement makes the requirement visible to the linker and removes a failure path.")),
        TestCase("S-03", "stack", "Scenario tree depth 10 -> 14 [compute]", "compute",
                 "Increase the recursive scenario tree depth from 10 to 14.",
                 "Does data-dependent recursion depth drive stack usage?",
                 baseline=C("depth=10"), variant=C("depth=14", depth=14), expect="INCREASES",
                 measure_stack=True, regime="small", same_output=False,
                 insight=("Each level keeps two local history arrays (~0.5 KB) alive; stack grows linearly "
                          "with depth while run time grows 16x. Unbounded recursion has no place in firmware.")),
        TestCase("S-04", "stack", "Tail-recursive horizon 1000 -> 4000 at -O2 [compute]", "compute",
                 "Quadruple the recursive forecast horizon with tail-call optimisation enabled (-O2).",
                 "Does recursion depth cost stack when the compiler turns tail calls into loops?",
                 baseline=C("horizon=1000", horizon=1000), variant=C("horizon=4000", horizon=4000),
                 expect="NEUTRAL", measure_stack=True, regime="small", same_output=False,
                 insight=("At -O2 the tail call becomes a jump: stack is constant in the horizon. The same "
                          "source at -O0 uses one frame per step (see S-05) -- the stack bound depends on the "
                          "build flags, so it must be verified for the shipping configuration.")),
        TestCase("S-05", "stack", "Tail-recursive horizon 1000 -> 4000 at -O0 [compute]", "compute",
                 "Same horizons as S-04 but built at -O0 (no tail-call elimination).",
                 "Recursion depth without the compiler's help.",
                 baseline=C("horizon=1000 -O0", ("-O0",), horizon=1000),
                 variant=C("horizon=4000 -O0", ("-O0",), horizon=4000), expect="INCREASES",
                 measure_stack=True, regime="small", same_output=False,
                 insight="Without sibling-call optimisation every step keeps a frame: stack grows linearly."),
        TestCase("S-06", "stack", f"Fits in a {cfg['stack_limit_kb']} KB stack? [compute]", "compute",
                 f"Run builds of the compute unit with the stack rlimit set to {cfg['stack_limit_kb']} KB "
                 "(ulimit -s), emulating a small RTOS task stack.",
                 "Which build configurations survive a small fixed stack?",
                 kind="limit", regime="small", expect="",
                 variants=[Variant("-O2", "compute", rlimits=(("STACK", lim),)),
                           Variant("-O0", "compute", cflags=("-O0",), rlimits=(("STACK", lim),)),
                           Variant("-O2 -fno-optimize-sibling-calls", "compute",
                                   cflags=("-O2", "-fno-optimize-sibling-calls"), rlimits=(("STACK", lim),)),
                           Variant("-Os", "compute", cflags=("-Os",), rlimits=(("STACK", lim),)),
                           Variant("-O2 scratch=stack", "compute", args=(("scratch", "stack"),),
                                   rlimits=(("STACK", lim),))],
                 insight=("A SIGSEGV here is a stack overflow. The same source passes or fails depending on "
                          "the optimisation flags: stack budgets must be proven per build configuration.")),
    ]


def suite_scaling(cfg):
    pairs = [
        ("C-01", "io", "I/O unit: store-everything vs ring buffer",
         [Variant("grow", "io"), Variant("ring", "io", args=(("strategy", "ring"),))]),
        ("C-02", "mem", "Memory unit: copy_sort vs inplace vs streaming",
         [Variant("copy_sort", "mem"), Variant("inplace", "mem", args=(("strategy", "inplace"),)),
          Variant("streaming", "mem", args=(("strategy", "streaming"),))]),
        ("C-03", "compute", "Compute unit: materialized vs streaming fit",
         [Variant("materialized", "compute"), Variant("streaming", "compute", args=(("mode", "streaming"),))]),
        ("C-04", "pipeline", "Pipeline: junior-dev vs overlay+streaming",
         [Variant("concurrent", "pipeline"),
          Variant("overlay+streaming", "pipeline", args=(("mode", "overlay"), ("fit", "streaming")))]),
    ]
    return [TestCase(tid, "scaling", title, unit,
                     f"Run each configuration at N = {', '.join(f'{x:,}' for x in cfg['scaling_ns'])} and fit "
                     "maxRSS = floor + slope x N.",
                     "How does memory grow with the amount of data (i.e. with uptime between uploads)?",
                     kind="scaling", variants=v, expect="",
                     insight=("The slope (bytes per sample) is the design's true memory cost. A slope near zero "
                              "means memory is bounded and the device can run indefinitely; any positive slope "
                              "is a maximum uptime before it runs out of RAM."))
            for tid, unit, title, v in pairs]


def suite_budget(cfg):
    lim = cfg["budget_mb"] * 1024 * 1024
    P = lambda label, mode, fit: Variant(label, "pipeline", args=(("mode", mode), ("fit", fit)),
                                          rlimits=(("AS", lim),))
    return [TestCase("B-01", "budget", f"Which pipeline fits a {cfg['budget_mb']} MB device?", "pipeline",
                     f"Run each pipeline memory plan with the address-space rlimit set to {cfg['budget_mb']} MB "
                     f"(N={cfg['n_large']:,}), emulating a small embedded Linux target.",
                     "Pass/fail under a hard memory budget, the way the product would actually fail.",
                     kind="limit", expect="",
                     variants=[P("concurrent/materialized", "concurrent", "materialized"),
                               P("phased/materialized", "phased", "materialized"),
                               P("overlay/materialized", "overlay", "materialized"),
                               P("phased/streaming", "phased", "streaming"),
                               P("overlay/streaming", "overlay", "streaming")],
                     insight=("RLIMIT_AS caps virtual address space, so malloc returns NULL exactly as on a "
                              "device without swap. A configuration either fits or it does not; there is no "
                              "'mostly fits' in an unattended machine room."))]


SUITES = {
    "flags": suite_flags, "data": suite_data, "alloc": suite_alloc, "algo": suite_algo,
    "overlay": suite_overlay, "stack": suite_stack, "scaling": suite_scaling, "budget": suite_budget,
}
SUITE_ORDER = ["flags", "data", "alloc", "algo", "overlay", "stack", "scaling", "budget"]
SUITE_TITLES = {
    "flags": "Compiler & linker flags, one at a time",
    "data": "Data representation (types and struct layout)",
    "alloc": "Allocation strategy (heap / static / bounded) and allocator policy",
    "algo": "Algorithm choice for the same job",
    "overlay": "Phase lifetime: concurrent vs phased vs overlay",
    "stack": "Stack usage and stack budgets",
    "scaling": "Memory vs data volume",
    "budget": "Hard memory budget (deployability)",
}


def build_all(cfg, suites, only=None):
    tests = []
    for s in SUITE_ORDER:
        if s in suites:
            tests.extend(SUITES[s](cfg))
    if only:
        wanted = {t.strip().upper() for t in only}
        tests = [t for t in tests if t.tid.upper() in wanted or any(t.tid.upper().startswith(w) for w in wanted)]
    return tests
