# Critter Memory Lab -- results summary

**Question:** What are the biggest impacts to memory usage?

**Answer (auto-generated from the data):** The largest single impact was F-LARGE-05 (-static at production volume [mem]): -656 KB (-2.0%) in max RSS. Shipping-relevant compiler/linker flags moved max RSS by at most 0 KB (-fconserve-stack) at small N. At production volume the biggest flag effect was 656 KB (2.0%). Flags shape the image and the stack; data structures and buffer lifetimes decide resident memory.

## Test environment

| item | value |
|---|---|
| host | Raspberry Pi 5 Model B Rev 1.1 (aarch64) |
| OS / kernel | Debian GNU/Linux 13 (trixie) / 6.18.50+rpt-rpi-2712 |
| page size | 16384 B |
| compiler | gcc (Debian 14.2.0-19) 14.2.0 |
| libc | glibc 2.41 |
| measurement | GNU time -v |
| repeats | 10 |
| small / large N | 20,000 / 1,000,000 |
| process floor | 1,088 KB |

**Classification rule.** A change counts only if it exceeds the noise threshold: max RSS needs max(2 pages, 2x run-to-run spread, 0.5%); image/heap/stack sizes are deterministic and use 0.5%/0.5%/2%. Overall verdict = resident verdict if it moved, else stack, else image.

## REDUCES memory (12)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| F-IO-41 | -flto -fwhole-program  [io] | 0 KB (+0.0%) | -3,205 B (-15.1%) | 0 B (+0.0%) | CONFIRMED |
| F-LIO-04 | -flto at production volume [io] | 0 KB (+0.0%) | -3,205 B (-15.1%) | - | REFUTED |
| F-LIO-02 | -Os at production volume [io] | 0 KB (+0.0%) | -1,297 B (-6.1%) | - | REFUTED |
| F-COM-41 | -flto -fwhole-program  [compute] | 0 KB (+0.0%) | -2,855 B (-4.5%) | -16 B (-0.2%) | CONFIRMED |
| F-LCOM-04 | -flto at production volume [compute] | 0 KB (+0.0%) | -2,855 B (-4.5%) | - | REFUTED |
| F-MEM-41 | -flto -fwhole-program  [mem] | 0 KB (+0.0%) | -2,903 B (-2.8%) | -16 B (-0.5%) | CONFIRMED |
| F-LARGE-04 | -flto at production volume [mem] | -16 KB (-0.0%) | -2,903 B (-2.8%) | - | REFUTED |
| F-LIO-05 | -static at production volume [io] | -544 KB (-2.2%) | +561.3 KB (+2709.9%) | - | CONFIRMED |
| F-LARGE-05 | -static at production volume [mem] | -656 KB (-2.0%) | +569.1 KB (+570.0%) | - | CONFIRMED |
| F-LCOM-02 | -Os at production volume [compute] | 0 KB (+0.0%) | -1,148 B (-1.8%) | - | REFUTED |
| F-LARGE-02 | -Os at production volume [mem] | 0 KB (+0.0%) | -1,256 B (-1.2%) | - | REFUTED |
| F-IO-40 | -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [io] | 0 KB (+0.0%) | -208 B (-1.0%) | 0 B (+0.0%) | CONFIRMED |

## INCREASES memory (7)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| F-LARGE-03 | -O3 at production volume [mem] | 0 KB (+0.0%) | +1,772 B (+1.7%) | - | REFUTED |
| F-LARGE-01 | -O0 at production volume [mem] | 0 KB (+0.0%) | +4,016 B (+3.9%) | - | REFUTED |
| F-LCOM-03 | -O3 at production volume [compute] | 0 KB (+0.0%) | +3,044 B (+4.8%) | - | REFUTED |
| F-LCOM-01 | -O0 at production volume [compute] | 0 KB (+0.0%) | +4,084 B (+6.4%) | - | REFUTED |
| F-LIO-03 | -O3 at production volume [io] | 0 KB (+0.0%) | +1,516 B (+7.1%) | - | REFUTED |
| F-LIO-01 | -O0 at production volume [io] | 0 KB (+0.0%) | +3,188 B (+15.0%) | - | REFUTED |
| F-LCOM-05 | -static at production volume [compute] | -544 KB (-0.4%) | +557.9 KB (+895.4%) | - | REFUTED |

## NEUTRAL memory (17)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| F-IO-37 | -fconserve-stack  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-IO-38 | -falign-functions=1  [io] | 0 KB (+0.0%) | -64 B (-0.3%) | 0 B (+0.0%) | REFUTED |
| F-IO-39 | -falign-loops=1  [io] | 0 KB (+0.0%) | -72 B (-0.3%) | 0 B (+0.0%) | REFUTED |
| F-IO-42 | -Wl,-z,norelro  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-IO-43 | -Wl,-z,noseparate-code  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-37 | -fconserve-stack  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-38 | -falign-functions=1  [mem] | 0 KB (+0.0%) | -64 B (-0.1%) | 0 B (+0.0%) | REFUTED |
| F-MEM-39 | -falign-loops=1  [mem] | 0 KB (+0.0%) | -72 B (-0.1%) | 0 B (+0.0%) | REFUTED |
| F-MEM-40 | -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [mem] | 0 KB (+0.0%) | -212 B (-0.2%) | 0 B (+0.0%) | REFUTED |
| F-MEM-42 | -Wl,-z,norelro  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-43 | -Wl,-z,noseparate-code  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-37 | -fconserve-stack  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-38 | -falign-functions=1  [compute] | 0 KB (+0.0%) | -64 B (-0.1%) | 0 B (+0.0%) | REFUTED |
| F-COM-39 | -falign-loops=1  [compute] | 0 KB (+0.0%) | -40 B (-0.1%) | 0 B (+0.0%) | REFUTED |
| F-COM-40 | -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [compute] | 0 KB (+0.0%) | -176 B (-0.3%) | 0 B (+0.0%) | REFUTED |
| F-COM-42 | -Wl,-z,norelro  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-43 | -Wl,-z,noseparate-code  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |

## Biggest impacts

| rank | test | change | max RSS delta | N |
|---|---|---|---|---|
| 1 | F-LARGE-05 | -static at production volume [mem] | -656 KB (-2.0%) | 1,000,000 |
| 2 | F-LIO-05 | -static at production volume [io] | -544 KB (-2.2%) | 1,000,000 |
| 3 | F-LCOM-05 | -static at production volume [compute] | -544 KB (-0.4%) | 1,000,000 |
| 4 | F-LARGE-04 | -flto at production volume [mem] | -16 KB (-0.0%) | 1,000,000 |
| 5 | F-IO-37 | -fconserve-stack  [io] | 0 KB (+0.0%) | 20,000 |
| 6 | F-IO-38 | -falign-functions=1  [io] | 0 KB (+0.0%) | 20,000 |
| 7 | F-IO-39 | -falign-loops=1  [io] | 0 KB (+0.0%) | 20,000 |
| 8 | F-IO-40 | -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [io] | 0 KB (+0.0%) | 20,000 |
| 9 | F-IO-41 | -flto -fwhole-program  [io] | 0 KB (+0.0%) | 20,000 |
| 10 | F-IO-42 | -Wl,-z,norelro  [io] | 0 KB (+0.0%) | 20,000 |
| 11 | F-IO-43 | -Wl,-z,noseparate-code  [io] | 0 KB (+0.0%) | 20,000 |
| 12 | F-MEM-37 | -fconserve-stack  [mem] | 0 KB (+0.0%) | 20,000 |

## Lever size by category

| category | largest effect | % of baseline | via |
|---|---|---|---|
| flags | 656 KB | 2.0% | F-LARGE-05 -static |
| flags (small N) | 0 KB | 0.0% | F-IO-37 -fconserve-stack |

## Refuted hypotheses (discussion material)

- **F-IO-37 -fconserve-stack  [io]**: expected REDUCES, observed NEUTRAL.
- **F-IO-38 -falign-functions=1  [io]**: expected REDUCES, observed NEUTRAL.
- **F-IO-39 -falign-loops=1  [io]**: expected REDUCES, observed NEUTRAL.
- **F-IO-42 -Wl,-z,norelro  [io]**: expected REDUCES, observed NEUTRAL.
- **F-IO-43 -Wl,-z,noseparate-code  [io]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-37 -fconserve-stack  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-38 -falign-functions=1  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-39 -falign-loops=1  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-40 -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-42 -Wl,-z,norelro  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-43 -Wl,-z,noseparate-code  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-COM-37 -fconserve-stack  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-COM-38 -falign-functions=1  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-COM-39 -falign-loops=1  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-COM-40 -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-COM-42 -Wl,-z,norelro  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-COM-43 -Wl,-z,noseparate-code  [compute]**: expected REDUCES, observed NEUTRAL.
- **F-LARGE-01 -O0 at production volume [mem]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LARGE-02 -Os at production volume [mem]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LARGE-03 -O3 at production volume [mem]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LARGE-04 -flto at production volume [mem]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LIO-01 -O0 at production volume [io]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LIO-02 -Os at production volume [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LIO-03 -O3 at production volume [io]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LIO-04 -flto at production volume [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LCOM-01 -O0 at production volume [compute]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LCOM-02 -Os at production volume [compute]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LCOM-03 -O3 at production volume [compute]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LCOM-04 -flto at production volume [compute]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LCOM-05 -static at production volume [compute]**: expected REDUCES, observed INCREASES (image only).

## Per-test write-ups

### F-IO-37 -- -fconserve-stack  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fconserve-stack'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fconserve-stack' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Asks GCC to minimise stack use, mainly by refusing inlining that would grow a caller's frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-38 -- -falign-functions=1  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-falign-functions=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (-64 B (-0.3%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding GCC inserts so each function starts on a cache-line-friendly boundary. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-39 -- -falign-loops=1  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-falign-loops=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-loops=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.6 KB (-72 B (-0.3%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding inserted before loop heads. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-40 -- -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.5 KB (-208 B (-1.0%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1' lowers image text+data+bss by 208 B (1.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. All code-alignment padding removed together. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-208 B (-1.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-41 -- -flto -fwhole-program  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-flto -fwhole-program'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto -fwhole-program' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 17.6 KB (-3,205 B (-15.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto -fwhole-program' lowers image text+data+bss by 3,205 B (15.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. LTO plus the promise that the program is complete: every function except main becomes local, so unused externally visible code can be discarded. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-3,205 B (-15.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-42 -- -Wl,-z,norelro  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-Wl,-z,norelro'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,norelro' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Drops the RELRO segment, which is page-aligned and made read-only after relocation; with 16 KB pages its alignment can cost a page. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-43 -- -Wl,-z,noseparate-code  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-Wl,-z,noseparate-code'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,noseparate-code' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Lets the linker place code and read-only data in fewer page-aligned segments, removing padding that 16 KB pages make expensive. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-37 -- -fconserve-stack  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fconserve-stack'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fconserve-stack' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Asks GCC to minimise stack use, mainly by refusing inlining that would grow a caller's frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-38 -- -falign-functions=1  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-falign-functions=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (-64 B (-0.1%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding GCC inserts so each function starts on a cache-line-friendly boundary. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-39 -- -falign-loops=1  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-falign-loops=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-loops=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (-72 B (-0.1%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding inserted before loop heads. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-40 -- -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.6 KB (-212 B (-0.2%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). All code-alignment padding removed together. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-41 -- -flto -fwhole-program  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-flto -fwhole-program'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto -fwhole-program' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 97.0 KB (-2,903 B (-2.8%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,952 B (-16 B (-0.5%), NEUTRAL)
- **Meaning:** '-flto -fwhole-program' lowers image text+data+bss by 2,903 B (2.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. LTO plus the promise that the program is complete: every function except main becomes local, so unused externally visible code can be discarded. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,903 B (-2.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-42 -- -Wl,-z,norelro  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-Wl,-z,norelro'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,norelro' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Drops the RELRO segment, which is page-aligned and made read-only after relocation; with 16 KB pages its alignment can cost a page. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-43 -- -Wl,-z,noseparate-code  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-Wl,-z,noseparate-code'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,noseparate-code' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Lets the linker place code and read-only data in fewer page-aligned segments, removing padding that 16 KB pages make expensive. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-37 -- -fconserve-stack  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fconserve-stack'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fconserve-stack' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Asks GCC to minimise stack use, mainly by refusing inlining that would grow a caller's frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-38 -- -falign-functions=1  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-falign-functions=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.2 KB (-64 B (-0.1%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding GCC inserts so each function starts on a cache-line-friendly boundary. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-39 -- -falign-loops=1  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-falign-loops=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-loops=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (-40 B (-0.1%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Removes the padding inserted before loop heads. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-40 -- -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.1 KB (-176 B (-0.3%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). All code-alignment padding removed together. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-41 -- -flto -fwhole-program  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-flto -fwhole-program'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto -fwhole-program' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 59.5 KB (-2,855 B (-4.5%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,296 B (-16 B (-0.2%), NEUTRAL)
- **Meaning:** '-flto -fwhole-program' lowers image text+data+bss by 2,855 B (4.5%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. LTO plus the promise that the program is complete: every function except main becomes local, so unused externally visible code can be discarded. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,855 B (-4.5%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-42 -- -Wl,-z,norelro  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-Wl,-z,norelro'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,norelro' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Drops the RELRO segment, which is page-aligned and made read-only after relocation; with 16 KB pages its alignment can cost a page. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-43 -- -Wl,-z,noseparate-code  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-Wl,-z,noseparate-code'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Wl,-z,noseparate-code' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Lets the linker place code and read-only data in fewer page-aligned segments, removing padding that 16 KB pages make expensive. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-01 -- -O0 at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit (outlier removal + summaries) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O0' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 103.8 KB (+4,016 B (+3.9%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O0' raises image text+data+bss by 4,016 B (3.9%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+4,016 B (+3.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Run time changed +62% (0.320 s -> 0.520 s): a memory/time trade-off to weigh, not ignore. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-02 -- -Os at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit (outlier removal + summaries) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-Os' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.6 KB (-1,256 B (-1.2%), REDUCES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,256 B (1.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-1,256 B (-1.2%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-03 -- -O3 at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit (outlier removal + summaries) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O3' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 101.6 KB (+1,772 B (+1.7%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 1,772 B (1.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+1,772 B (+1.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-04 -- -flto at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit (outlier removal + summaries) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-flto' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (-16 KB (-0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 97.0 KB (-2,903 B (-2.8%), REDUCES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 2,903 B (2.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-2,903 B (-2.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-05 -- -static at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit (outlier removal + summaries) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-static' still matter?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 30.9 MB (-656 KB (-2.0%), REDUCES); image text+data+bss: 99.8 KB -> 669.0 KB (+569.1 KB (+570.0%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 656 KB (2.0%) versus '-O2 (baseline)'. Static linking removes a FIXED cost (shared libc mapping, loader, relocations), so it saves about the same absolute amount at any N -- a shrinking percentage as data grow. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 2.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+569.1 KB (+570.0%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+569.1 KB (+570.0%)).

### F-LIO-01 -- -O0 at production volume [io]

- **Test:** Same comparison as the small-N flag tests, but the I/O unit (high-rate acquisition) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O0' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 23.8 KB (+3,188 B (+15.0%), INCREASES); tracked heap peak: 24.02 MB -> 24.02 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O0' raises image text+data+bss by 3,188 B (15.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+3,188 B (+15.0%)) is paid in full in flash/RAM, which Linux demand paging hides. Run time changed +267% (0.030 s -> 0.110 s): a memory/time trade-off to weigh, not ignore. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LIO-02 -- -Os at production volume [io]

- **Test:** Same comparison as the small-N flag tests, but the I/O unit (high-rate acquisition) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-Os' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 19.4 KB (-1,297 B (-6.1%), REDUCES); tracked heap peak: 24.02 MB -> 24.02 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,297 B (6.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-1,297 B (-6.1%)) is paid in full in flash/RAM, which Linux demand paging hides. Run time changed +33% (0.030 s -> 0.040 s): a memory/time trade-off to weigh, not ignore. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LIO-03 -- -O3 at production volume [io]

- **Test:** Same comparison as the small-N flag tests, but the I/O unit (high-rate acquisition) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O3' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 22.2 KB (+1,516 B (+7.1%), INCREASES); tracked heap peak: 24.02 MB -> 24.02 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 1,516 B (7.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+1,516 B (+7.1%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LIO-04 -- -flto at production volume [io]

- **Test:** Same comparison as the small-N flag tests, but the I/O unit (high-rate acquisition) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-flto' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 17.6 KB (-3,205 B (-15.1%), REDUCES); tracked heap peak: 24.02 MB -> 24.02 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 3,205 B (15.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-3,205 B (-15.1%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LIO-05 -- -static at production volume [io]

- **Test:** Same comparison as the small-N flag tests, but the I/O unit (high-rate acquisition) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-static' still matter?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 23.5 MB (-544 KB (-2.2%), REDUCES); image text+data+bss: 20.7 KB -> 582.0 KB (+561.3 KB (+2709.9%), INCREASES); tracked heap peak: 24.02 MB -> 24.02 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 544 KB (2.2%) versus '-O2 (baseline)'. Static linking removes a FIXED cost (shared libc mapping, loader, relocations), so it saves about the same absolute amount at any N -- a shrinking percentage as data grow. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 2.2% of what the Critter must provision. On an MMU-less microcontroller the image change (+561.3 KB (+2709.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+561.3 KB (+2709.9%)).

### F-LCOM-01 -- -O0 at production volume [compute]

- **Test:** Same comparison as the small-N flag tests, but the compute unit (HVAC prediction) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O0' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 138.5 MB -> 138.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 66.3 KB (+4,084 B (+6.4%), INCREASES); tracked heap peak: 137.37 MB -> 137.37 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O0' raises image text+data+bss by 4,084 B (6.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+4,084 B (+6.4%)) is paid in full in flash/RAM, which Linux demand paging hides. Run time changed +43% (0.420 s -> 0.600 s): a memory/time trade-off to weigh, not ignore. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LCOM-02 -- -Os at production volume [compute]

- **Test:** Same comparison as the small-N flag tests, but the compute unit (HVAC prediction) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-Os' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 138.5 MB -> 138.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 61.2 KB (-1,148 B (-1.8%), REDUCES); tracked heap peak: 137.37 MB -> 137.37 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,148 B (1.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-1,148 B (-1.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LCOM-03 -- -O3 at production volume [compute]

- **Test:** Same comparison as the small-N flag tests, but the compute unit (HVAC prediction) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O3' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 138.5 MB -> 138.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 65.3 KB (+3,044 B (+4.8%), INCREASES); tracked heap peak: 137.37 MB -> 137.37 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 3,044 B (4.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+3,044 B (+4.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LCOM-04 -- -flto at production volume [compute]

- **Test:** Same comparison as the small-N flag tests, but the compute unit (HVAC prediction) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-flto' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 138.5 MB -> 138.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 59.5 KB (-2,855 B (-4.5%), REDUCES); tracked heap peak: 137.37 MB -> 137.37 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 2,855 B (4.5%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-2,855 B (-4.5%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LCOM-05 -- -static at production volume [compute]

- **Test:** Same comparison as the small-N flag tests, but the compute unit (HVAC prediction) processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-static' still matter?
- **Hypothesis:** REDUCES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 138.5 MB -> 138.0 MB (-544 KB (-0.4%), NEUTRAL); image text+data+bss: 62.3 KB -> 620.2 KB (+557.9 KB (+895.4%), INCREASES); tracked heap peak: 137.37 MB -> 137.37 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' raises image text+data+bss by 557.9 KB (895.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Static linking removes a FIXED cost (shared libc mapping, loader, relocations), so it saves about the same absolute amount at any N -- a shrinking percentage as data grow. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 0.4% of what the Critter must provision. On an MMU-less microcontroller the image change (+557.9 KB (+895.4%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

