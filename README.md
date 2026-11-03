# Critter Memory Lab

A test harness for the question **"What are the biggest impacts to memory usage?"**, built around the Critter machine-room monitor and its three units: I/O, memory and compute. Every experiment builds two configurations, runs each under `/usr/bin/time -v`, and reports four things in a fixed format: what the test was, what was being tested, what the outcome was, and what it means. It then classifies the change as **REDUCES**, **INCREASES** or **NEUTRAL**.

## Quick start (Raspberry Pi 5, Raspberry Pi OS)

```bash
sudo apt install build-essential time binutils python3   # GNU time is the 'time -v' the assignment asks for
cd critter-memlab
python3 run_memlab.py --list            # every test, with its hypothesis
python3 run_memlab.py --quick           # first look: N=200k, 3 repeats (~2-4 min)
python3 run_memlab.py --repeats 10 --no-aslr   # report-quality run (default N=1,000,000)
```

Useful options:

| option | effect |
|---|---|
| `--suite algo,overlay` | run only some suites (`flags,data,alloc,algo,overlay,stack,scaling,budget`) |
| `--only F-COM,S-06` | run tests whose id starts with these prefixes |
| `--units mem` | restrict the per-flag suite to one unit |
| `--n-large 2000000` | data volume for the data-dominated tests |
| `--budget-mb 64` | memory budget for the deployability test |
| `--stack-limit-kb 64` | stack budget for the stack-overflow test |
| `--no-stack-probe` | skip stack high-water builds (faster) |

Python 3.8+ standard library only, with no pip installs needed.

## Layout

```
run_memlab.py          CLI entry point
memlab/
  env.py               platform probe (page size, compiler, libc, governor, ASLR)
  build.py             one binary per configuration + size(1)/nm/-fstack-usage analysis
  runner.py            runs under GNU time -v, parses it, repeats, aggregates
  testcases.py         EVERY experiment, declared as data (edit/add here)
  analysis.py          noise-aware classification and the "MEANING" text
  report.py            terminal output and all log files
  core.py              orchestration
src/
  critter_common.[ch]  sensor model, tracked heap, overlay arena, stack probe, /proc reporting
  critter_algo.[ch]    quickselect, summaries, matmul, Gaussian elimination
  unit_io.c            I/O unit
  unit_mem.c           memory unit
  unit_compute.c       compute unit
  pipeline.c           all three units in one process (phase-lifetime / overlay studies)
  noop.c               empty program: the process floor
tools/ctime.c          stand-in for GNU time if it is not installed (same output fields)
Makefile               manual builds for poking around (the harness does its own)
```

## The units

Each unit's default configuration is the junior-developer prototype, and every optimisation is measured against it.

| unit | default (baseline) | alternatives | knobs |
|---|---|---|---|
| **io**: 100 Hz acquisition into records, window summaries | `--strategy=grow` (realloc doubling) | `heap` (exact malloc), `static` (.bss), `ring` (bounded W-window) | `-DCRITTER_SAMPLE_TYPE=0/1/2` (double/float/int16), `-DCRITTER_LAYOUT=0/1/2` (naive/reordered/packed struct) |
| **mem**: robust outlier removal (median/MAD), summaries | `--strategy=copy_sort` (4 N-sized buffers) | `inplace` (quickselect), `histogram` (fixed 80 KB), `streaming` (per-window) | sample type |
| **compute**: AR(p) HVAC prediction, recursive forecast, scenario tree | `--mode=materialized` (X, explicit Xᵀ, matmul) | `--mode=streaming` (accumulate XᵀX) | `--scratch=heap/stack/static`, `--horizon`, `--depth`, `--p` |
| **pipeline**: acquire → clean → predict | `--mode=concurrent` (all buffers live) | `phased`, `overlay` (one planned arena), `--stage=` (one process per phase) | `--fit=materialized/streaming` |

The sensor is deterministic: a 22 °C setpoint, a compressor cycle, drift, noise and ~0.1% ADC spikes. That means every run sees identical data, and each unit prints a checksum of its output. When a test should not change results (e.g. a compiler flag), the harness verifies the checksum matches.

## What is measured, and why

| metric | source | why an embedded engineer cares |
|---|---|---|
| **max RSS** | `time -v` "Maximum resident set size" | Peak physical RAM, which is what the device must provision. This is the primary metric. |
| **image** (text+data+bss) | `size` on the ELF | What an MCU linker script must fit. Linux demand-paging hides most of it; flash/SRAM does not. |
| **tracked heap peak** | `malloc_usable_size()` accounting in `cm_malloc` | What the program *requested*. The difference from RSS shows untouched reservations and hidden library allocations. |
| **stack high-water** | stack painting in a separate `-DCRITTER_STACK_PROBE` build | The worst-case stack depth, which must fit an RTOS task stack. |
| minor/major faults, run time | `time -v` | First-touch page cost and the memory/time trade-off. |
| file size, `.eh_frame`, worst frame (`.su`), largest symbols | ELF + `-fstack-usage` + `nm` | Logged in `builds.log` to explain *why* the image changed. |
| phase snapshots | `/proc/self/status` at phase boundaries | RSS over time inside a run, written to `phases.csv`. |

## Suites

| suite | question | example finding to look for |
|---|---|---|
| `flags` | Each compiler/linker flag *individually*, added to -O2, at small N (code-dominated), plus five headline flags at production N | Most flags move the image by KB and RSS by nothing; `-static` lowers RSS but balloons the image; `-fno-optimize-sibling-calls` and `-O1` blow up the stack |
| `data` | Types and struct layout | Reordering struct fields is a free 33% |
| `alloc` | grow vs exact vs static vs ring buffer; allocator policy | Untouched capacity costs address space, not RAM; ring buffers make memory independent of uptime |
| `algo` | Same job, different algorithm | Streaming the fit removes >90% of compute memory |
| `overlay` | Buffer lifetimes: concurrent / phased / planned overlay / one process per phase | Overlays cut peak from Σphases to max(phase) and no further |
| `stack` | Heap→stack, recursion depth, tail calls, and a hard 128 KB stack limit | The same source passes or segfaults depending on -O level |
| `scaling` | RSS vs N, fitted as floor + slope·N | Bytes per retained sample turns into "hours of uptime before OOM" |
| `budget` | Pass/fail under an address-space rlimit | Which designs actually deploy on a small device |

A negative control (`-pipe`, which only changes how gcc passes temp files) is included in the flag suite. If it ever shows a change, the noise threshold is too tight.

## Reading a test block

```
[F-COM-29] -fno-optimize-sibling-calls  [compute]    (suite: flags)
  TEST      : Build the compute unit at -O2 and again with '-fno-optimize-sibling-calls'; run each 5x ...
  TESTING   : Does '-fno-optimize-sibling-calls' change resident memory, image size or stack depth?
  HYPOTHESIS: INCREASES
  BASELINE  : -O2 (baseline)               -O2
  VARIANT   : -fno-optimize-sibling-calls  -O2 -fno-optimize-sibling-calls
  RESULTS   : metric                    baseline     variant   delta                 verdict
             max RSS (time -v)           5,036 KB    4,992 KB   -44 KB (-0.9%)        NEUTRAL (+/-208 KB)
             image text+data+bss          63.4 KB     63.5 KB   +16 B (+0.0%)         NEUTRAL
             stack high-water             7,448 B    188.1 KB   +180.8 KB             INCREASES
  OUTCOME   : INCREASES (stack only)   hypothesis INCREASES -> CONFIRMED   output: identical
  MEANING   : ... the recursive forecast keeps one frame per step instead of becoming a loop ...
```

### Classification rule

* **max RSS** must move by more than `max(2 pages, 2 × run-to-run spread, 0.5%)`.
* **image** must move by more than `max(32 B, 0.5%)`; **heap** by more than `max(64 B, 0.5%)`; **stack** by more than `max(64 B, 2%)`. These three are deterministic.
* **Overall** is the RSS verdict if RSS moved. Otherwise it is the stack verdict ("stack only"), and otherwise the image verdict ("image only"). A dimension that moved the other way is reported as a **trade-off**.

## Log files

Every run writes `logs/memlab_<timestamp>/`:

| file | contents |
|---|---|
| `console.log` | Exact terminal transcript |
| `summary.md` | Report-ready: environment, REDUCES/INCREASES/NEUTRAL tables, biggest impacts, lever size by category, scaling and budget tables, refuted hypotheses, per-test write-ups |
| `results.csv` | One row per test, with every metric, verdict, hypothesis result and meaning text |
| `results.json` | The same, plus phase snapshots and the environment |
| `runs_raw.csv` | Every single execution (for error bars and plots) |
| `phases.csv` | RSS/heap at each phase boundary of every run (memory over time) |
| `builds.log` | Compiler command, section sizes, largest symbols and worst stack frame for every binary |

## Measurement caveats (put these in the report)

1. **`time -v` on Linux only fills in Maximum RSS.** The "Average … size" fields are always 0 because the kernel does not provide integral RSS.
2. **Pi 5 kernels use 16 KB pages** (`getconf PAGESIZE`). RSS moves in 16 KB steps, so code-size changes of a few KB are often invisible in RSS. That is why the image is measured separately.
3. **Only touched memory is resident.** `malloc(100 MB)` or a 100 MB `.bss` array costs no RSS until written, which is why A-01/A-02 can be RSS-neutral while heap or image change.
4. **Measurement must not perturb the system.** The stack probe paints ~1 MB of stack, so probe builds are used only for the stack metric. `/proc` is read without malloc. Heap accounting adds no headers.
5. **Max RSS survives `exec()`.** A child forked straight from the Python harness would report the harness's own RSS. That is why runs go through GNU time (or `tools/ctime`), a tiny intermediate process.
6. **Library code allocates too.** glibc's `qsort` can malloc a temporary as large as the array (merge sort), so compare RSS against the tracked heap in G-01.
7. **`RLIMIT_AS` limits virtual memory**, which is stricter than RSS (it includes reserved-but-untouched mappings). That is appropriate for "will malloc fail on a small device".
8. **`-fpack-struct` is deliberately excluded.** Applied globally it changes the ABI of libc structs. Packing is tested where it is safe, on the record type (D-04).
9. Fix the CPU governor (`performance`) if you also report timing. Memory numbers are unaffected.

## Adding an experiment

Append a `TestCase` in `memlab/testcases.py`:

```python
TestCase("G-05", "algo", "My idea [mem]", "mem",
         what="Run the memory unit with --strategy=myidea.",
         testing="Does my idea beat inplace?",
         baseline=Variant("inplace", "mem", args=(("strategy", "inplace"),)),
         variant=Variant("myidea", "mem", args=(("strategy", "myidea"),)),
         expect="REDUCES", insight="Why it should work...", same_output=True)
```

A variant can change `cflags`, `ldflags`, `defines`, `args`, `env` or `rlimits`. The harness handles building, repeats, statistics, classification and logging.

## Mapping results to the assignment

* **"Use the three units and identify memory used with time -v":** baseline rows of the `data`, `alloc` and `algo` suites, plus the `scaling` tables.
* **"Specific optimisation flags, not just the groups":** the `flags` suite tests 30+ individual flags against -O2, with -O0/-O1/-O3/-Os/-Oz/-Og for context.
* **"Reduce the amount of stack or heap":** the `alloc`, `algo` and `stack` suites.
* **"Overlays":** the `overlay` suite (planned data overlay arena, and one process per phase as the OS-level overlay).
* **"Which reduce, increase, are neutral":** the three tables at the top of `summary.md`.
* **"Biggest impacts":** the "Biggest impacts" and "Lever size by category" sections, plus the auto-generated answer paragraph.

## HW4 follow-up run (grader requests)

`hw4_followup.sh` collects only the new data requested after grading, in one pass (about 10-20 minutes on a Pi 5):

1. The seven new flags (`-fconserve-stack`, `-falign-functions=1`, `-falign-loops=1`, all `-falign-*=1` together,
   `-flto -fwhole-program`, `-Wl,-z,norelro`, `-Wl,-z,noseparate-code`) on all three units (tests F-*-37 to F-*-43).
2. The five production-volume flags (`-O0`, `-Os`, `-O3`, `-flto`, `-static` at N = 1,000,000) on the I/O and
   compute units as well as the memory unit (F-LIO-*, F-LCOM-*, F-LARGE-*).
3. Raw `time -v` output for each unit's baseline at N = 1,000,000 (`timev_*.txt`).
4. The FORTIFY investigation: max RSS x10, `/proc/self/smaps` at exit (via `tools/smapsdump.c`), program headers,
   imported `_chk` symbols and, if installed, an `strace` of mappings, for plain and `-D_FORTIFY_SOURCE=2` builds of
   the I/O unit and the empty program.

```bash
sudo apt install strace     # optional but useful for the FORTIFY check
bash hw4_followup.sh        # produces followup_<timestamp>.zip
```
