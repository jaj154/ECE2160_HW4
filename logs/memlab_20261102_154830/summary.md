# Critter Memory Lab -- results summary

**Question:** What are the biggest impacts to memory usage?

**Answer (auto-generated from the data):** The largest single impact was O-04 (Overlay + streaming fit (shrink the dominant phase)): -137.5 MB (-89.5%) in max RSS. Shipping-relevant compiler/linker flags moved max RSS by at most 1,056 KB (-static) at small N. At production volume the biggest flag effect was 656 KB (2.0%). Design choices (representation, buffering, algorithm, phase lifetime) moved it by up to 137.5 MB (90%, O-04). Flags shape the image and the stack; data structures and buffer lifetimes decide resident memory.

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

## REDUCES memory (44)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| G-04 | materialized matrix -> streaming normal equations [compute] | -137.5 MB (-99.2%) | 0 B (+0.0%) | - | CONFIRMED |
| G-03 | batch -> streaming windows [mem] | -30.5 MB (-96.7%) | 0 B (+0.0%) | - | CONFIRMED |
| A-03 | Store-everything -> bounded ring buffer [io] | -23.0 MB (-95.6%) | 0 B (+0.0%) | - | CONFIRMED |
| O-04 | Overlay + streaming fit (shrink the dominant phase) | -137.5 MB (-89.5%) | 0 B (+0.0%) | - | CONFIRMED |
| G-02 | copy+qsort -> fixed histogram [mem] | -23.0 MB (-72.9%) | 0 B (+0.0%) | - | CONFIRMED |
| D-02 | Sample type double -> fixed16 [io] | -11.5 MB (-47.8%) | +264 B (+1.2%) | - | CONFIRMED |
| G-01 | copy+qsort -> quickselect in place [mem] | -15.0 MB (-47.5%) | 0 B (+0.0%) | - | CONFIRMED |
| D-04 | Record layout naive -> packed [io] | -9,728 KB (-39.5%) | +40 B (+0.2%) | - | CONFIRMED |
| D-06 | Sample type double -> fixed16 [mem] | -11.4 MB (-36.3%) | +376 B (+0.4%) | - | CONFIRMED |
| F-IO-20 | -static  [io] | -496 KB (-31.3%) | +561.3 KB (+2709.9%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-20 | -static  [mem] | -496 KB (-31.3%) | +569.1 KB (+570.0%) | 0 B (+0.0%) | CONFIRMED |
| D-01 | Sample type double -> float [io] | -7,680 KB (-31.2%) | -40 B (-0.2%) | - | CONFIRMED |
| D-03 | Record layout naive -> reordered [io] | -7,680 KB (-31.2%) | -168 B (-0.8%) | - | CONFIRMED |
| F-COM-20 | -static  [compute] | -1,056 KB (-25.5%) | +557.9 KB (+895.4%) | 0 B (+0.0%) | CONFIRMED |
| D-05 | Sample type double -> float [mem] | -7,808 KB (-24.2%) | +104 B (+0.1%) | - | CONFIRMED |
| F-IO-14 | -flto  [io] | 0 KB (+0.0%) | -3,205 B (-15.1%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-13 | -ffunction-sections -fdata-sections -Wl,--gc-sections  [io] | 0 KB (+0.0%) | -2,301 B (-10.8%) | 0 B (+0.0%) | CONFIRMED |
| O-02 | All buffers live -> data overlay arena | -15.5 MB (-10.1%) | 0 B (+0.0%) | - | CONFIRMED |
| O-05 | Single process -> one process per phase (exec overlay) | -15.5 MB (-10.1%) | - | - | CONFIRMED |
| O-01 | All buffers live -> free when dead (phased) | -15.2 MB (-9.9%) | 0 B (+0.0%) | - | CONFIRMED |
| F-IO-15 | -fno-asynchronous-unwind-tables -fno-unwind-tables  [io] | 0 KB (+0.0%) | -1,692 B (-8.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-04 | -Os  [io] | 0 KB (+0.0%) | -1,297 B (-6.1%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-05 | -Oz  [io] | 0 KB (+0.0%) | -1,297 B (-6.1%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-14 | -flto  [compute] | 0 KB (+0.0%) | -2,855 B (-4.5%) | -16 B (-0.2%) | CONFIRMED |
| D-07 | Input type double -> fixed16 [compute] | -6,144 KB (-4.3%) | +336 B (+0.5%) | - | CONFIRMED |
| F-COM-13 | -ffunction-sections -fdata-sections -Wl,--gc-sections  [compute] | 0 KB (+0.0%) | -2,163 B (-3.4%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-15 | -fno-asynchronous-unwind-tables -fno-unwind-tables  [compute] | 0 KB (+0.0%) | -1,812 B (-2.8%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-14 | -flto  [mem] | 0 KB (+0.0%) | -2,903 B (-2.8%) | -16 B (-0.5%) | CONFIRMED |
| F-LARGE-04 | -flto at production volume [mem] | -16 KB (-0.0%) | -2,903 B (-2.8%) | - | REFUTED |
| F-COM-28 | -fomit-frame-pointer  [compute] | 0 KB (+0.0%) | -184 B (-0.3%) | -192 B (-2.6%) | REFUTED |
| F-COM-19 | -fno-pie -no-pie  [compute] | 0 KB (+0.0%) | -433 B (-0.7%) | -176 B (-2.4%) | CONFIRMED |
| F-IO-02 | -O1  [io] | 0 KB (+0.0%) | -504 B (-2.4%) | +32 B (+1.1%) | REFUTED |
| F-IO-19 | -fno-pie -no-pie  [io] | 0 KB (+0.0%) | -441 B (-2.1%) | 0 B (+0.0%) | CONFIRMED |
| F-LARGE-05 | -static at production volume [mem] | -656 KB (-2.0%) | +569.1 KB (+570.0%) | - | CONFIRMED |
| F-MEM-13 | -ffunction-sections -fdata-sections -Wl,--gc-sections  [mem] | 0 KB (+0.0%) | -1,879 B (-1.8%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-04 | -Os  [compute] | 0 KB (+0.0%) | -1,148 B (-1.8%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-05 | -Oz  [compute] | 0 KB (+0.0%) | -1,148 B (-1.8%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-15 | -fno-asynchronous-unwind-tables -fno-unwind-tables  [mem] | 0 KB (+0.0%) | -1,788 B (-1.7%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-04 | -Os  [mem] | 0 KB (+0.0%) | -1,256 B (-1.2%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-05 | -Oz  [mem] | 0 KB (+0.0%) | -1,256 B (-1.2%) | 0 B (+0.0%) | CONFIRMED |
| F-LARGE-02 | -Os at production volume [mem] | 0 KB (+0.0%) | -1,256 B (-1.2%) | - | REFUTED |
| F-IO-31 | -ffast-math  [io] | 0 KB (+0.0%) | -242 B (-1.1%) | 0 B (+0.0%) | REFUTED |
| F-IO-33 | -fPIC  [io] | 0 KB (+0.0%) | -160 B (-0.8%) | 0 B (+0.0%) | REFUTED |
| F-IO-28 | -fomit-frame-pointer  [io] | 0 KB (+0.0%) | -152 B (-0.7%) | 0 B (+0.0%) | REFUTED |

## INCREASES memory (48)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| F-MEM-24 | -fstack-protector-strong  [mem] | 0 KB (+0.0%) | +629 B (+0.6%) | -16 B (-0.5%) | CONFIRMED |
| F-MEM-18 | -fno-plt  [mem] | 0 KB (+0.0%) | +712 B (+0.7%) | +16 B (+0.5%) | REFUTED |
| F-COM-10 | -fno-inline  [compute] | 0 KB (+0.0%) | +532 B (+0.8%) | +80 B (+1.1%) | REFUTED |
| F-COM-18 | -fno-plt  [compute] | 0 KB (+0.0%) | +576 B (+0.9%) | 0 B (+0.0%) | REFUTED |
| F-MEM-09 | -finline-limit=1000  [mem] | 0 KB (+0.0%) | +988 B (+1.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-11 | -ftree-vectorize -fvect-cost-model=dynamic  [mem] | 0 KB (+0.0%) | +1,052 B (+1.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-03 | -O3  [mem] | 0 KB (+0.0%) | +1,772 B (+1.7%) | 0 B (+0.0%) | CONFIRMED |
| F-LARGE-03 | -O3 at production volume [mem] | 0 KB (+0.0%) | +1,772 B (+1.7%) | - | REFUTED |
| F-COM-11 | -ftree-vectorize -fvect-cost-model=dynamic  [compute] | 0 KB (+0.0%) | +1,140 B (+1.8%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-23 | -fstack-protector-all  [compute] | 0 KB (+0.0%) | +3,009 B (+4.7%) | +168 B (+2.3%) | CONFIRMED |
| F-COM-24 | -fstack-protector-strong  [compute] | 0 KB (+0.0%) | +597 B (+0.9%) | +168 B (+2.3%) | CONFIRMED |
| F-IO-24 | -fstack-protector-strong  [io] | 0 KB (+0.0%) | +549 B (+2.6%) | -16 B (-0.6%) | CONFIRMED |
| F-IO-18 | -fno-plt  [io] | 0 KB (+0.0%) | +616 B (+2.9%) | 0 B (+0.0%) | REFUTED |
| F-MEM-23 | -fstack-protector-all  [mem] | 0 KB (+0.0%) | +3,025 B (+3.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-10 | -fno-inline  [mem] | 0 KB (+0.0%) | +676 B (+0.7%) | +96 B (+3.2%) | REFUTED |
| F-IO-11 | -ftree-vectorize -fvect-cost-model=dynamic  [io] | 0 KB (+0.0%) | +724 B (+3.4%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-06 | -Og  [mem] | 0 KB (+0.0%) | +48 B (+0.0%) | +112 B (+3.8%) | CONFIRMED |
| F-LARGE-01 | -O0 at production volume [mem] | 0 KB (+0.0%) | +4,016 B (+3.9%) | - | REFUTED |
| F-IO-09 | -finline-limit=1000  [io] | 0 KB (+0.0%) | +988 B (+4.7%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-03 | -O3  [compute] | 0 KB (+0.0%) | +3,044 B (+4.8%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-10 | -fno-inline  [io] | 0 KB (+0.0%) | +268 B (+1.3%) | +144 B (+5.0%) | REFUTED |
| F-MEM-01 | -O0  [mem] | 0 KB (+0.0%) | +4,016 B (+3.9%) | +160 B (+5.4%) | CONFIRMED |
| A-04 | Allocator policy: mmap threshold raised [pipeline/phased] | +7,840 KB (+5.5%) | 0 B (+0.0%) | - | CONFIRMED |
| F-IO-01 | -O0  [io] | 0 KB (+0.0%) | +3,188 B (+15.0%) | +160 B (+5.5%) | CONFIRMED |
| F-IO-06 | -Og  [io] | 0 KB (+0.0%) | -436 B (-2.1%) | +160 B (+5.5%) | CONFIRMED |
| F-IO-03 | -O3  [io] | 0 KB (+0.0%) | +1,516 B (+7.1%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-07 | -funroll-loops  [mem] | +16 KB (+1.0%) | +9,348 B (+9.1%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-08 | -funroll-all-loops  [mem] | +16 KB (+1.0%) | +10,000 B (+9.8%) | +16 B (+0.5%) | CONFIRMED |
| F-COM-07 | -funroll-loops  [compute] | +16 KB (+0.4%) | +7,852 B (+12.3%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-26 | -D_FORTIFY_SOURCE=2  [compute] | +512 KB (+12.4%) | +83 B (+0.1%) | 0 B (+0.0%) | REFUTED |
| F-COM-08 | -funroll-all-loops  [compute] | +16 KB (+0.4%) | +8,368 B (+13.1%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-23 | -fstack-protector-all  [io] | 0 KB (+0.0%) | +2,881 B (+13.6%) | -16 B (-0.6%) | CONFIRMED |
| F-IO-26 | -D_FORTIFY_SOURCE=2  [io] | +512 KB (+32.3%) | +83 B (+0.4%) | -16 B (-0.6%) | REFUTED |
| F-MEM-26 | -D_FORTIFY_SOURCE=2  [mem] | +512 KB (+32.3%) | +83 B (+0.1%) | -16 B (-0.5%) | REFUTED |
| F-IO-07 | -funroll-loops  [io] | +16 KB (+1.0%) | +6,948 B (+32.8%) | 0 B (+0.0%) | CONFIRMED |
| S-03 | Scenario tree depth 10 -> 14 [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | +2,432 B (+33.3%) | CONFIRMED |
| F-IO-08 | -funroll-all-loops  [io] | +16 KB (+1.0%) | +7,464 B (+35.2%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-09 | -finline-limit=1000  [compute] | 0 KB (+0.0%) | +3,308 B (+5.2%) | +3,664 B (+50.1%) | CONFIRMED |
| F-COM-36 | -fsanitize=address  [compute] | +7,232 KB (+174.5%) | +19.2 KB (+30.8%) | - | CONFIRMED |
| S-05 | Tail-recursive horizon 1000 -> 4000 at -O0 [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | +234.4 KB (+297.1%) | CONFIRMED |
| F-MEM-36 | -fsanitize=address  [mem] | +6,720 KB (+424.2%) | +16.4 KB (+16.4%) | - | CONFIRMED |
| F-IO-36 | -fsanitize=address  [io] | +7,232 KB (+456.6%) | +15.9 KB (+76.7%) | - | CONFIRMED |
| S-01 | Solver workspace heap -> stack [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | +40.3 KB (+563.9%) | CONFIRMED |
| F-COM-02 | -O1  [compute] | 0 KB (+0.0%) | -312 B (-0.5%) | +55.9 KB (+783.2%) | REFUTED |
| F-COM-29 | -fno-optimize-sibling-calls  [compute] | 0 KB (+0.0%) | +40 B (+0.1%) | +55.9 KB (+783.4%) | CONFIRMED |
| F-COM-06 | -Og  [compute] | 0 KB (+0.0%) | -204 B (-0.3%) | +56.0 KB (+784.2%) | CONFIRMED |
| F-COM-01 | -O0  [compute] | 0 KB (+0.0%) | +4,084 B (+6.4%) | +306.1 KB (+4286.9%) | CONFIRMED |
| A-02 | Growable vector -> static .bss buffer [io] | 0 KB (+0.0%) | +22.89 MB (+113154.7%) | - | REFUTED |

## NEUTRAL memory (46)

| test | change | max RSS delta | image delta | stack delta | hypothesis |
|---|---|---|---|---|---|
| O-03 | Phased (allocator) -> overlay (planned) | -352 KB (-0.2%) | 0 B (+0.0%) | - | CONFIRMED |
| F-IO-12 | -fipa-cp-clone  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-IO-16 | -fmerge-all-constants  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-17 | -fshort-enums  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-21 | -s  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-22 | -g  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-25 | -fstack-clash-protection  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-IO-27 | -fno-omit-frame-pointer  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-IO-29 | -fno-optimize-sibling-calls  [io] | 0 KB (+0.0%) | -16 B (-0.1%) | +48 B (+1.7%) | REFUTED |
| F-IO-30 | -mcpu=native  [io] | 0 KB (+0.0%) | -40 B (-0.2%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-32 | -fvisibility=hidden  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-34 | -fno-common  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-IO-35 | -pipe  [io] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-02 | -O1  [mem] | 0 KB (+0.0%) | -352 B (-0.3%) | +32 B (+1.1%) | CONFIRMED |
| F-MEM-12 | -fipa-cp-clone  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-16 | -fmerge-all-constants  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-17 | -fshort-enums  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-19 | -fno-pie -no-pie  [mem] | 0 KB (+0.0%) | -481 B (-0.5%) | 0 B (+0.0%) | REFUTED |
| F-MEM-21 | -s  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-22 | -g  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-25 | -fstack-clash-protection  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-27 | -fno-omit-frame-pointer  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-MEM-28 | -fomit-frame-pointer  [mem] | 0 KB (+0.0%) | -216 B (-0.2%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-29 | -fno-optimize-sibling-calls  [mem] | 0 KB (+0.0%) | -16 B (-0.0%) | +48 B (+1.6%) | REFUTED |
| F-MEM-30 | -mcpu=native  [mem] | 0 KB (+0.0%) | -40 B (-0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-31 | -ffast-math  [mem] | 0 KB (+0.0%) | -330 B (-0.3%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-32 | -fvisibility=hidden  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-33 | -fPIC  [mem] | 0 KB (+0.0%) | -160 B (-0.2%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-34 | -fno-common  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-MEM-35 | -pipe  [mem] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-12 | -fipa-cp-clone  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-16 | -fmerge-all-constants  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-17 | -fshort-enums  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-21 | -s  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-22 | -g  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-25 | -fstack-clash-protection  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-27 | -fno-omit-frame-pointer  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | REFUTED |
| F-COM-30 | -mcpu=native  [compute] | 0 KB (+0.0%) | -40 B (-0.1%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-31 | -ffast-math  [compute] | 0 KB (+0.0%) | -122 B (-0.2%) | -16 B (-0.2%) | CONFIRMED |
| F-COM-32 | -fvisibility=hidden  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-33 | -fPIC  [compute] | 0 KB (+0.0%) | -160 B (-0.3%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-34 | -fno-common  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| F-COM-35 | -pipe  [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| A-01 | Growable vector -> exact heap allocation [io] | 0 KB (+0.0%) | 0 B (+0.0%) | - | REFUTED |
| S-02 | Solver workspace heap -> static [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |
| S-04 | Tail-recursive horizon 1000 -> 4000 at -O2 [compute] | 0 KB (+0.0%) | 0 B (+0.0%) | 0 B (+0.0%) | CONFIRMED |

## Biggest impacts

| rank | test | change | max RSS delta | N |
|---|---|---|---|---|
| 1 | O-04 | Overlay + streaming fit (shrink the dominant phase) | -137.5 MB (-89.5%) | 1,000,000 |
| 2 | G-04 | materialized matrix -> streaming normal equations [compute] | -137.5 MB (-99.2%) | 1,000,000 |
| 3 | G-03 | batch -> streaming windows [mem] | -30.5 MB (-96.7%) | 1,000,000 |
| 4 | G-02 | copy+qsort -> fixed histogram [mem] | -23.0 MB (-72.9%) | 1,000,000 |
| 5 | A-03 | Store-everything -> bounded ring buffer [io] | -23.0 MB (-95.6%) | 1,000,000 |
| 6 | O-02 | All buffers live -> data overlay arena | -15.5 MB (-10.1%) | 1,000,000 |
| 7 | O-05 | Single process -> one process per phase (exec overlay) | -15.5 MB (-10.1%) | 1,000,000 |
| 8 | O-01 | All buffers live -> free when dead (phased) | -15.2 MB (-9.9%) | 1,000,000 |
| 9 | G-01 | copy+qsort -> quickselect in place [mem] | -15.0 MB (-47.5%) | 1,000,000 |
| 10 | D-02 | Sample type double -> fixed16 [io] | -11.5 MB (-47.8%) | 1,000,000 |
| 11 | D-06 | Sample type double -> fixed16 [mem] | -11.4 MB (-36.3%) | 1,000,000 |
| 12 | D-04 | Record layout naive -> packed [io] | -9,728 KB (-39.5%) | 1,000,000 |

## Lever size by category

| category | largest effect | % of baseline | via |
|---|---|---|---|
| overlay | 137.5 MB | 89.5% | O-04 overlay+streaming |
| algo | 137.5 MB | 99.2% | G-04 streaming |
| alloc | 23.0 MB | 95.6% | A-03 ring |
| data | 11.5 MB | 47.8% | D-02 fixed16 |
| flags (small N) | 7,232 KB | 456.6% | F-IO-36 -fsanitize=address |
| flags | 656 KB | 2.0% | F-LARGE-05 -static |
| stack (small N) | 0 KB | 0.0% | S-01 scratch=stack |

## S-06 Fits in a 128 KB stack? [compute]

| configuration | result | max RSS |
|---|---|---|
| -O2 | PASS | 4,144 KB |
| -O0 | FAIL: SIGSEGV (stack overflow?) | - |
| -O2 -fno-optimize-sibling-calls | PASS | 4,144 KB |
| -Os | PASS | 4,144 KB |
| -O2 scratch=stack | PASS | 4,144 KB |

Of 5 configurations, 4 fit the limit. A SIGSEGV here is a stack overflow. The same source passes or fails depending on the optimisation flags: stack budgets must be proven per build configuration.

## C-01 I/O unit: store-everything vs ring buffer

| configuration | N=125,000 | N=250,000 | N=500,000 | N=1,000,000 | verdict |
|---|---|---|---|---|---|
| grow | 4,144 KB | 7,216 KB | 12.5 MB | 24.0 MB | O(N): 23.9 B/sample; a 64 MB budget holds ~2,754,622 samples (~7.7 h at 100 Hz) |
| ring | 1,088 KB | 1,088 KB | 1,088 KB | 1,088 KB | BOUNDED (memory independent of N) |

## C-02 Memory unit: copy_sort vs inplace vs streaming

| configuration | N=125,000 | N=250,000 | N=500,000 | N=1,000,000 | verdict |
|---|---|---|---|---|---|
| copy_sort | 4,816 KB | 8,816 KB | 16.4 MB | 31.5 MB | O(N): 32.1 B/sample; a 64 MB budget holds ~2,056,544 samples (~5.7 h at 100 Hz) |
| inplace | 3,120 KB | 5,168 KB | 8,752 KB | 16.5 MB | O(N): 16.1 B/sample; a 64 MB budget holds ~4,091,974 samples (~11.4 h at 100 Hz) |
| streaming | 1,088 KB | 1,088 KB | 1,088 KB | 1,088 KB | BOUNDED (memory independent of N) |

## C-03 Compute unit: materialized vs streaming fit

| configuration | N=125,000 | N=250,000 | N=500,000 | N=1,000,000 | verdict |
|---|---|---|---|---|---|
| materialized | 18.0 MB | 35.5 MB | 69.5 MB | 138.5 MB | O(N): 144.2 B/sample; a 64 MB budget holds ~458,414 samples (~1.3 h at 100 Hz) |
| streaming | 1,088 KB | 1,088 KB | 1,088 KB | 1,088 KB | BOUNDED (memory independent of N) |

## C-04 Pipeline: junior-dev vs overlay+streaming

| configuration | N=125,000 | N=250,000 | N=500,000 | N=1,000,000 | verdict |
|---|---|---|---|---|---|
| concurrent | 20.0 MB | 39.0 MB | 77.5 MB | 153.5 MB | O(N): 160.0 B/sample; a 64 MB budget holds ~412,751 samples (~1.1 h at 100 Hz) |
| overlay+streaming | 3,120 KB | 5,168 KB | 8,752 KB | 16.0 MB | O(N): 15.5 B/sample; a 64 MB budget holds ~4,245,358 samples (~11.8 h at 100 Hz) |

## B-01 Which pipeline fits a 64 MB device?

| configuration | result | max RSS |
|---|---|---|
| concurrent/materialized | FAIL: OOM | - |
| phased/materialized | FAIL: OOM | - |
| overlay/materialized | FAIL: OOM | - |
| phased/streaming | PASS | 24.0 MB |
| overlay/streaming | PASS | 16.0 MB |

Of 5 configurations, 2 fit the limit. RLIMIT_AS caps virtual address space, so malloc returns NULL exactly as on a device without swap. A configuration either fits or it does not; there is no 'mostly fits' in an unattended machine room.

## Refuted hypotheses (discussion material)

- **F-IO-02 -O1  [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-IO-10 -fno-inline  [io]**: expected REDUCES, observed INCREASES (stack only).
- **F-IO-12 -fipa-cp-clone  [io]**: expected INCREASES, observed NEUTRAL.
- **F-IO-18 -fno-plt  [io]**: expected NEUTRAL, observed INCREASES (image only).
- **F-IO-25 -fstack-clash-protection  [io]**: expected INCREASES, observed NEUTRAL.
- **F-IO-26 -D_FORTIFY_SOURCE=2  [io]**: expected NEUTRAL, observed INCREASES (resident).
- **F-IO-27 -fno-omit-frame-pointer  [io]**: expected INCREASES, observed NEUTRAL.
- **F-IO-28 -fomit-frame-pointer  [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-IO-29 -fno-optimize-sibling-calls  [io]**: expected INCREASES, observed NEUTRAL.
- **F-IO-31 -ffast-math  [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-IO-33 -fPIC  [io]**: expected NEUTRAL, observed REDUCES (image only).
- **F-MEM-10 -fno-inline  [mem]**: expected REDUCES, observed INCREASES (stack only).
- **F-MEM-12 -fipa-cp-clone  [mem]**: expected INCREASES, observed NEUTRAL.
- **F-MEM-18 -fno-plt  [mem]**: expected NEUTRAL, observed INCREASES (image only).
- **F-MEM-19 -fno-pie -no-pie  [mem]**: expected REDUCES, observed NEUTRAL.
- **F-MEM-25 -fstack-clash-protection  [mem]**: expected INCREASES, observed NEUTRAL.
- **F-MEM-26 -D_FORTIFY_SOURCE=2  [mem]**: expected NEUTRAL, observed INCREASES (resident).
- **F-MEM-27 -fno-omit-frame-pointer  [mem]**: expected INCREASES, observed NEUTRAL.
- **F-MEM-29 -fno-optimize-sibling-calls  [mem]**: expected INCREASES, observed NEUTRAL.
- **F-COM-02 -O1  [compute]**: expected NEUTRAL, observed INCREASES (stack only).
- **F-COM-10 -fno-inline  [compute]**: expected REDUCES, observed INCREASES (image only).
- **F-COM-12 -fipa-cp-clone  [compute]**: expected INCREASES, observed NEUTRAL.
- **F-COM-18 -fno-plt  [compute]**: expected NEUTRAL, observed INCREASES (image only).
- **F-COM-25 -fstack-clash-protection  [compute]**: expected INCREASES, observed NEUTRAL.
- **F-COM-26 -D_FORTIFY_SOURCE=2  [compute]**: expected NEUTRAL, observed INCREASES (resident).
- **F-COM-27 -fno-omit-frame-pointer  [compute]**: expected INCREASES, observed NEUTRAL.
- **F-COM-28 -fomit-frame-pointer  [compute]**: expected NEUTRAL, observed REDUCES (stack only).
- **F-LARGE-01 -O0 at production volume [mem]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LARGE-02 -Os at production volume [mem]**: expected NEUTRAL, observed REDUCES (image only).
- **F-LARGE-03 -O3 at production volume [mem]**: expected NEUTRAL, observed INCREASES (image only).
- **F-LARGE-04 -flto at production volume [mem]**: expected NEUTRAL, observed REDUCES (image only).
- **A-01 Growable vector -> exact heap allocation [io]**: expected REDUCES, observed NEUTRAL.
- **A-02 Growable vector -> static .bss buffer [io]**: expected REDUCES, observed INCREASES (image only).

## Per-test write-ups

### F-IO-01 -- -O0  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-O0'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O0' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 23.8 KB (+3,188 B (+15.0%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 3,048 B (+160 B (+5.5%), INCREASES)
- **Meaning:** '-O0' raises stack high-water by 160 B (5.5%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. No register allocation: every local lives in a stack slot, nothing is inlined and tail calls are not eliminated, so frames and code both grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+3,188 B (+15.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-02 -- -O1  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-O1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O1' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.2 KB (-504 B (-2.4%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,920 B (+32 B (+1.1%), NEUTRAL)
- **Meaning:** '-O1' lowers image text+data+bss by 504 B (2.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -O1 drops the inlining heuristics and IPA passes of -O2, so code is similar in size and data are untouched. Watch the stack: -foptimize-sibling-calls is an -O2 pass, so tail recursion is NOT removed at -O1. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-504 B (-2.4%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-03 -- -O3  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-O3'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O3' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 22.2 KB (+1,516 B (+7.1%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 1,516 B (7.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -O3 adds aggressive inlining, loop versioning, unswitching and vectorisation; each duplicates code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+1,516 B (+7.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-04 -- -Os  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-Os'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Os' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 19.4 KB (-1,297 B (-6.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,297 B (6.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Os is -O2 minus size-increasing passes (alignment padding, unrolling, most inlining). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,297 B (-6.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-05 -- -Oz  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-Oz'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Oz' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 19.4 KB (-1,297 B (-6.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Oz' lowers image text+data+bss by 1,297 B (6.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Oz (GCC 12+) minimises size even at a speed cost (e.g. no function alignment, call-heavy code). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,297 B (-6.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-06 -- -Og  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-Og'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Og' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.3 KB (-436 B (-2.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 3,048 B (+160 B (+5.5%), INCREASES)
- **Meaning:** '-Og' raises stack high-water by 160 B (5.5%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Og keeps variables observable for the debugger and, like -O1, leaves tail calls as real calls. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-436 B (-2.1%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss REDUCES (-436 B (-2.1%)).

### F-IO-07 -- -funroll-loops  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-funroll-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,600 KB (+16 KB (+1.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 27.5 KB (+6,948 B (+32.8%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-funroll-loops' raises image text+data+bss by 6,948 B (32.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolling replicates loop bodies to cut branch overhead: a pure code-for-speed trade. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+6,948 B (+32.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-08 -- -funroll-all-loops  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-funroll-all-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-all-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,600 KB (+16 KB (+1.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 28.0 KB (+7,464 B (+35.2%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-funroll-all-loops' raises image text+data+bss by 7,464 B (35.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolls even loops with unknown trip counts, adding remainder loops as well. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+7,464 B (+35.2%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-09 -- -finline-limit=1000  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-finline-limit=1000'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-finline-limit=1000' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 21.7 KB (+988 B (+4.7%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-finline-limit=1000' raises image text+data+bss by 988 B (4.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Raises the inlining budget, so callee bodies are copied into every call site. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+988 B (+4.7%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-10 -- -fno-inline  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-inline'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-inline' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 21.0 KB (+268 B (+1.3%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 3,032 B (+144 B (+5.0%), INCREASES)
- **Meaning:** '-fno-inline' raises stack high-water by 144 B (5.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Disables inlining: calls replace copies. Note the catch: small static inline helpers (s_to_c, c_to_s) then become out-of-line copies in every translation unit, so code can even grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+268 B (+1.3%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-11 -- -ftree-vectorize -fvect-cost-model=dynamic  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-ftree-vectorize -fvect-cost-model=dynamic'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ftree-vectorize -fvect-cost-model=dynamic' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 21.4 KB (+724 B (+3.4%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ftree-vectorize -fvect-cost-model=dynamic' raises image text+data+bss by 724 B (3.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. O3-style vectorisation: SIMD body plus scalar prologue/epilogue and runtime alias checks. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+724 B (+3.4%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-12 -- -fipa-cp-clone  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fipa-cp-clone'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fipa-cp-clone' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Clones functions specialised for constant arguments, trading code size for speed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-13 -- -ffunction-sections -fdata-sections -Wl,--gc-sections  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-ffunction-sections -fdata-sections -Wl,--gc-sections'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffunction-sections -fdata-sections -Wl,--gc-sections' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 18.5 KB (-2,301 B (-10.8%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ffunction-sections -fdata-sections -Wl,--gc-sections' lowers image text+data+bss by 2,301 B (10.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Each function/object in its own section lets the linker discard unreferenced ones. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,301 B (-10.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-14 -- -flto  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-flto'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 17.6 KB (-3,205 B (-15.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 3,205 B (15.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Link-time optimisation sees the whole program: removes dead code and specialises across units. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-3,205 B (-15.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-15 -- -fno-asynchronous-unwind-tables -fno-unwind-tables  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-asynchronous-unwind-tables -fno-unwind-tables'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-asynchronous-unwind-tables -fno-unwind-tables' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 19.1 KB (-1,692 B (-8.0%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-asynchronous-unwind-tables -fno-unwind-tables' lowers image text+data+bss by 1,692 B (8.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Drops .eh_frame unwind tables; C code without exceptions does not need them to run. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,692 B (-8.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-16 -- -fmerge-all-constants  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fmerge-all-constants'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fmerge-all-constants' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Merges identical constants and arrays across the program; few duplicates exist here. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-17 -- -fshort-enums  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fshort-enums'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fshort-enums' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Enums take the smallest integer type; no bulk data here is enum-typed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-18 -- -fno-plt  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-plt'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-plt' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 21.3 KB (+616 B (+2.9%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-plt' raises image text+data+bss by 616 B (2.9%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Calls shared-library functions through the GOT instead of PLT stubs; tiny, mixed effect. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+616 B (+2.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-19 -- -fno-pie -no-pie  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-pie -no-pie'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-pie -no-pie' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.3 KB (-441 B (-2.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-pie -no-pie' lowers image text+data+bss by 441 B (2.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Position-dependent executables need fewer dynamic relocations and GOT entries. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-441 B (-2.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-20 -- -static  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-static'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-static' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 1,584 KB -> 1,088 KB (-496 KB (-31.3%), REDUCES); image text+data+bss: 20.7 KB -> 582.0 KB (+561.3 KB (+2709.9%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 496 KB (31.3%) versus '-O2 (baseline)'. Static linking pulls libc into the image (image grows) but avoids mapping the shared libc, the loader and relocation of a single process (resident shrinks). Shared libraries only pay off when many processes share them. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+561.3 KB (+2709.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+561.3 KB (+2709.9%)).

### F-IO-21 -- -s  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-s'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-s' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Strips the symbol table: smaller file on disk, but symbols are never loaded, so RAM is unchanged. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-22 -- -g  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-g'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-g' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Debug info lives in non-allocated sections: the file grows, the resident image does not. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-23 -- -fstack-protector-all  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fstack-protector-all'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-all' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 23.5 KB (+2,881 B (+13.6%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,872 B (-16 B (-0.6%), NEUTRAL)
- **Meaning:** '-fstack-protector-all' raises image text+data+bss by 2,881 B (13.6%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. A canary slot and check sequence in every function: slightly larger frames and code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+2,881 B (+13.6%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-24 -- -fstack-protector-strong  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fstack-protector-strong'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-strong' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 21.2 KB (+549 B (+2.6%), INCREASES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,872 B (-16 B (-0.6%), NEUTRAL)
- **Meaning:** '-fstack-protector-strong' raises image text+data+bss by 549 B (2.6%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Canaries only in functions with local arrays or address-taken locals. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+549 B (+2.6%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-IO-25 -- -fstack-clash-protection  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fstack-clash-protection'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-clash-protection' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Probes each page of large stack allocations; adds code only where frames are large. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-26 -- -D_FORTIFY_SOURCE=2  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-D_FORTIFY_SOURCE=2'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-D_FORTIFY_SOURCE=2' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 1,584 KB -> 2,096 KB (+512 KB (+32.3%), INCREASES); image text+data+bss: 20.7 KB -> 20.8 KB (+83 B (+0.4%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,872 B (-16 B (-0.6%), NEUTRAL)
- **Meaning:** '-D_FORTIFY_SOURCE=2' raises max RSS (time -v) by 512 KB (32.3%) versus '-O2 (baseline)'. Bounds-checked variants of memcpy/strcpy etc. where sizes are known; a few extra bytes. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-27 -- -fno-omit-frame-pointer  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-omit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-omit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Keeps a frame pointer: one register lost and a save/restore per frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-28 -- -fomit-frame-pointer  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fomit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fomit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.6 KB (-152 B (-0.7%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fomit-frame-pointer' lowers image text+data+bss by 152 B (0.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Already enabled at -O1 and above on these targets; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-152 B (-0.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-29 -- -fno-optimize-sibling-calls  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-optimize-sibling-calls'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-optimize-sibling-calls' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (-16 B (-0.1%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,936 B (+48 B (+1.7%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Disables tail-call elimination: the recursive forecast keeps one frame per step instead of becoming a loop. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-30 -- -mcpu=native  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-mcpu=native'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-mcpu=native' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (-40 B (-0.2%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Tunes instruction selection for this exact CPU; code size and data size barely change. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-31 -- -ffast-math  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-ffast-math'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffast-math' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.5 KB (-242 B (-1.1%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ffast-math' lowers image text+data+bss by 242 B (1.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Relaxes IEEE rules; memory-neutral, but it may change numerical results (watch the checksum). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-242 B (-1.1%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-32 -- -fvisibility=hidden  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fvisibility=hidden'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fvisibility=hidden' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Hides symbols from the dynamic table; executables export very little anyway. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-33 -- -fPIC  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fPIC'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fPIC' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.6 KB (-160 B (-0.8%), REDUCES); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fPIC' lowers image text+data+bss by 160 B (0.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Library-style position independence in an executable: GOT-relative addressing, similar size. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-160 B (-0.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-IO-34 -- -fno-common  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fno-common'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-common' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Default since GCC 10; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-35 -- -pipe  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-pipe'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-pipe' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 784.0 KB -> 784.0 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,888 B -> 2,888 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). NEGATIVE CONTROL: -pipe only changes how the compiler passes temporary files. Any 'change' here is measurement noise, which validates the noise threshold. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-IO-36 -- -fsanitize=address  [io]

- **Test:** Build the I/O unit (high-rate acquisition) at -O2 and again with '-fsanitize=address'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fsanitize=address' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 1,584 KB -> 8,816 KB (+7,232 KB (+456.6%), INCREASES); image text+data+bss: 20.7 KB -> 36.6 KB (+15.9 KB (+76.7%), INCREASES); tracked heap peak: 784.0 KB -> 768.0 KB (-16.0 KB (-2.0%), REDUCES)
- **Meaning:** '-fsanitize=address' raises max RSS (time -v) by 7,232 KB (456.6%) versus '-O2 (baseline)'. AddressSanitizer: shadow memory (1/8 of address space reserved), redzones around every allocation and a quarantine of freed blocks. A debugging tool, never a shipping config. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+15.9 KB (+76.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: tracked heap peak REDUCES (-16.0 KB (-2.0%)).

### F-MEM-01 -- -O0  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-O0'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O0' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 103.8 KB (+4,016 B (+3.9%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 3,128 B (+160 B (+5.4%), INCREASES)
- **Meaning:** '-O0' raises stack high-water by 160 B (5.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. No register allocation: every local lives in a stack slot, nothing is inlined and tail calls are not eliminated, so frames and code both grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+4,016 B (+3.9%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-02 -- -O1  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-O1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O1' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.5 KB (-352 B (-0.3%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 3,000 B (+32 B (+1.1%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). -O1 drops the inlining heuristics and IPA passes of -O2, so code is similar in size and data are untouched. Watch the stack: -foptimize-sibling-calls is an -O2 pass, so tail recursion is NOT removed at -O1. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-03 -- -O3  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-O3'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O3' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 101.6 KB (+1,772 B (+1.7%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 1,772 B (1.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -O3 adds aggressive inlining, loop versioning, unswitching and vectorisation; each duplicates code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+1,772 B (+1.7%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-04 -- -Os  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-Os'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Os' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.6 KB (-1,256 B (-1.2%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,256 B (1.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Os is -O2 minus size-increasing passes (alignment padding, unrolling, most inlining). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,256 B (-1.2%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-05 -- -Oz  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-Oz'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Oz' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.6 KB (-1,256 B (-1.2%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Oz' lowers image text+data+bss by 1,256 B (1.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Oz (GCC 12+) minimises size even at a speed cost (e.g. no function alignment, call-heavy code). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,256 B (-1.2%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-06 -- -Og  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-Og'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Og' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.9 KB (+48 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 3,080 B (+112 B (+3.8%), INCREASES)
- **Meaning:** '-Og' raises stack high-water by 112 B (3.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Og keeps variables observable for the debugger and, like -O1, leaves tail calls as real calls. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-07 -- -funroll-loops  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-funroll-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,600 KB (+16 KB (+1.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 109.0 KB (+9,348 B (+9.1%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-funroll-loops' raises image text+data+bss by 9,348 B (9.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolling replicates loop bodies to cut branch overhead: a pure code-for-speed trade. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+9,348 B (+9.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-08 -- -funroll-all-loops  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-funroll-all-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-all-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,600 KB (+16 KB (+1.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 109.6 KB (+10,000 B (+9.8%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,984 B (+16 B (+0.5%), NEUTRAL)
- **Meaning:** '-funroll-all-loops' raises image text+data+bss by 10,000 B (9.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolls even loops with unknown trip counts, adding remainder loops as well. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+10,000 B (+9.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-09 -- -finline-limit=1000  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-finline-limit=1000'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-finline-limit=1000' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 100.8 KB (+988 B (+1.0%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-finline-limit=1000' raises image text+data+bss by 988 B (1.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Raises the inlining budget, so callee bodies are copied into every call site. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+988 B (+1.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-10 -- -fno-inline  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-inline'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-inline' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 100.5 KB (+676 B (+0.7%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 3,064 B (+96 B (+3.2%), INCREASES)
- **Meaning:** '-fno-inline' raises stack high-water by 96 B (3.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Disables inlining: calls replace copies. Note the catch: small static inline helpers (s_to_c, c_to_s) then become out-of-line copies in every translation unit, so code can even grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+676 B (+0.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-11 -- -ftree-vectorize -fvect-cost-model=dynamic  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-ftree-vectorize -fvect-cost-model=dynamic'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ftree-vectorize -fvect-cost-model=dynamic' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 100.9 KB (+1,052 B (+1.0%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ftree-vectorize -fvect-cost-model=dynamic' raises image text+data+bss by 1,052 B (1.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. O3-style vectorisation: SIMD body plus scalar prologue/epilogue and runtime alias checks. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+1,052 B (+1.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-12 -- -fipa-cp-clone  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fipa-cp-clone'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fipa-cp-clone' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Clones functions specialised for constant arguments, trading code size for speed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-13 -- -ffunction-sections -fdata-sections -Wl,--gc-sections  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-ffunction-sections -fdata-sections -Wl,--gc-sections'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffunction-sections -fdata-sections -Wl,--gc-sections' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.0 KB (-1,879 B (-1.8%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ffunction-sections -fdata-sections -Wl,--gc-sections' lowers image text+data+bss by 1,879 B (1.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Each function/object in its own section lets the linker discard unreferenced ones. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,879 B (-1.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-14 -- -flto  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-flto'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 97.0 KB (-2,903 B (-2.8%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,952 B (-16 B (-0.5%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 2,903 B (2.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Link-time optimisation sees the whole program: removes dead code and specialises across units. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,903 B (-2.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-15 -- -fno-asynchronous-unwind-tables -fno-unwind-tables  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-asynchronous-unwind-tables -fno-unwind-tables'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-asynchronous-unwind-tables -fno-unwind-tables' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.1 KB (-1,788 B (-1.7%), REDUCES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-asynchronous-unwind-tables -fno-unwind-tables' lowers image text+data+bss by 1,788 B (1.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Drops .eh_frame unwind tables; C code without exceptions does not need them to run. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,788 B (-1.7%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-16 -- -fmerge-all-constants  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fmerge-all-constants'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fmerge-all-constants' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Merges identical constants and arrays across the program; few duplicates exist here. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-17 -- -fshort-enums  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fshort-enums'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fshort-enums' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Enums take the smallest integer type; no bulk data here is enum-typed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-18 -- -fno-plt  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-plt'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-plt' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 100.5 KB (+712 B (+0.7%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,984 B (+16 B (+0.5%), NEUTRAL)
- **Meaning:** '-fno-plt' raises image text+data+bss by 712 B (0.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Calls shared-library functions through the GOT instead of PLT stubs; tiny, mixed effect. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+712 B (+0.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-19 -- -fno-pie -no-pie  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-pie -no-pie'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-pie -no-pie' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.4 KB (-481 B (-0.5%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Position-dependent executables need fewer dynamic relocations and GOT entries. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-20 -- -static  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-static'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-static' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 1,584 KB -> 1,088 KB (-496 KB (-31.3%), REDUCES); image text+data+bss: 99.8 KB -> 669.0 KB (+569.1 KB (+570.0%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 496 KB (31.3%) versus '-O2 (baseline)'. Static linking pulls libc into the image (image grows) but avoids mapping the shared libc, the loader and relocation of a single process (resident shrinks). Shared libraries only pay off when many processes share them. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+569.1 KB (+570.0%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+569.1 KB (+570.0%)).

### F-MEM-21 -- -s  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-s'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-s' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Strips the symbol table: smaller file on disk, but symbols are never loaded, so RAM is unchanged. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-22 -- -g  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-g'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-g' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Debug info lives in non-allocated sections: the file grows, the resident image does not. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-23 -- -fstack-protector-all  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fstack-protector-all'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-all' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 102.8 KB (+3,025 B (+3.0%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fstack-protector-all' raises image text+data+bss by 3,025 B (3.0%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. A canary slot and check sequence in every function: slightly larger frames and code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+3,025 B (+3.0%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-24 -- -fstack-protector-strong  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fstack-protector-strong'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-strong' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 100.5 KB (+629 B (+0.6%), INCREASES); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,952 B (-16 B (-0.5%), NEUTRAL)
- **Meaning:** '-fstack-protector-strong' raises image text+data+bss by 629 B (0.6%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Canaries only in functions with local arrays or address-taken locals. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+629 B (+0.6%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-MEM-25 -- -fstack-clash-protection  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fstack-clash-protection'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-clash-protection' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Probes each page of large stack allocations; adds code only where frames are large. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-26 -- -D_FORTIFY_SOURCE=2  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-D_FORTIFY_SOURCE=2'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-D_FORTIFY_SOURCE=2' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 1,584 KB -> 2,096 KB (+512 KB (+32.3%), INCREASES); image text+data+bss: 99.8 KB -> 99.9 KB (+83 B (+0.1%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,952 B (-16 B (-0.5%), NEUTRAL)
- **Meaning:** '-D_FORTIFY_SOURCE=2' raises max RSS (time -v) by 512 KB (32.3%) versus '-O2 (baseline)'. Bounds-checked variants of memcpy/strcpy etc. where sizes are known; a few extra bytes. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-27 -- -fno-omit-frame-pointer  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-omit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-omit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Keeps a frame pointer: one register lost and a save/restore per frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-28 -- -fomit-frame-pointer  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fomit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fomit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.6 KB (-216 B (-0.2%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Already enabled at -O1 and above on these targets; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-29 -- -fno-optimize-sibling-calls  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-optimize-sibling-calls'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-optimize-sibling-calls' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (-16 B (-0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 3,016 B (+48 B (+1.6%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Disables tail-call elimination: the recursive forecast keeps one frame per step instead of becoming a loop. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-MEM-30 -- -mcpu=native  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-mcpu=native'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-mcpu=native' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (-40 B (-0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Tunes instruction selection for this exact CPU; code size and data size barely change. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-31 -- -ffast-math  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-ffast-math'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffast-math' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.5 KB (-330 B (-0.3%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Relaxes IEEE rules; memory-neutral, but it may change numerical results (watch the checksum). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-32 -- -fvisibility=hidden  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fvisibility=hidden'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fvisibility=hidden' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Hides symbols from the dynamic table; executables export very little anyway. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-33 -- -fPIC  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fPIC'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fPIC' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.7 KB (-160 B (-0.2%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Library-style position independence in an executable: GOT-relative addressing, similar size. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-34 -- -fno-common  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fno-common'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-common' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Default since GCC 10; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-35 -- -pipe  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-pipe'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-pipe' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 1,584 KB -> 1,584 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 633.1 KB -> 633.1 KB (0 B (+0.0%), NEUTRAL); stack high-water: 2,968 B -> 2,968 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). NEGATIVE CONTROL: -pipe only changes how the compiler passes temporary files. Any 'change' here is measurement noise, which validates the noise threshold. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-MEM-36 -- -fsanitize=address  [mem]

- **Test:** Build the memory unit (outlier removal + summaries) at -O2 and again with '-fsanitize=address'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fsanitize=address' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 1,584 KB -> 8,304 KB (+6,720 KB (+424.2%), INCREASES); image text+data+bss: 99.8 KB -> 116.2 KB (+16.4 KB (+16.4%), INCREASES); tracked heap peak: 633.1 KB -> 625.6 KB (-7,672 B (-1.2%), REDUCES)
- **Meaning:** '-fsanitize=address' raises max RSS (time -v) by 6,720 KB (424.2%) versus '-O2 (baseline)'. AddressSanitizer: shadow memory (1/8 of address space reserved), redzones around every allocation and a quarantine of freed blocks. A debugging tool, never a shipping config. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+16.4 KB (+16.4%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: tracked heap peak REDUCES (-7,672 B (-1.2%)).

### F-COM-01 -- -O0  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-O0'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O0' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 66.3 KB (+4,084 B (+6.4%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 313.2 KB (+306.1 KB (+4286.9%), INCREASES)
- **Meaning:** '-O0' raises stack high-water by 306.1 KB (4286.9%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. No register allocation: every local lives in a stack slot, nothing is inlined and tail calls are not eliminated, so frames and code both grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+4,084 B (+6.4%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-02 -- -O1  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-O1'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O1' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.0 KB (-312 B (-0.5%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 63.1 KB (+55.9 KB (+783.2%), INCREASES)
- **Meaning:** '-O1' raises stack high-water by 55.9 KB (783.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -O1 drops the inlining heuristics and IPA passes of -O2, so code is similar in size and data are untouched. Watch the stack: -foptimize-sibling-calls is an -O2 pass, so tail recursion is NOT removed at -O1. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-03 -- -O3  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-O3'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-O3' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 65.3 KB (+3,044 B (+4.8%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 3,044 B (4.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -O3 adds aggressive inlining, loop versioning, unswitching and vectorisation; each duplicates code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+3,044 B (+4.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-04 -- -Os  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-Os'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Os' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 61.2 KB (-1,148 B (-1.8%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,148 B (1.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Os is -O2 minus size-increasing passes (alignment padding, unrolling, most inlining). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,148 B (-1.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-05 -- -Oz  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-Oz'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Oz' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 61.2 KB (-1,148 B (-1.8%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Oz' lowers image text+data+bss by 1,148 B (1.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Oz (GCC 12+) minimises size even at a speed cost (e.g. no function alignment, call-heavy code). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,148 B (-1.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-06 -- -Og  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-Og'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-Og' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.1 KB (-204 B (-0.3%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 63.1 KB (+56.0 KB (+784.2%), INCREASES)
- **Meaning:** '-Og' raises stack high-water by 56.0 KB (784.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. -Og keeps variables observable for the debugger and, like -O1, leaves tail calls as real calls. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-07 -- -funroll-loops  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-funroll-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,160 KB (+16 KB (+0.4%), NEUTRAL); image text+data+bss: 62.3 KB -> 70.0 KB (+7,852 B (+12.3%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-funroll-loops' raises image text+data+bss by 7,852 B (12.3%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolling replicates loop bodies to cut branch overhead: a pure code-for-speed trade. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+7,852 B (+12.3%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-08 -- -funroll-all-loops  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-funroll-all-loops'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-funroll-all-loops' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,160 KB (+16 KB (+0.4%), NEUTRAL); image text+data+bss: 62.3 KB -> 70.5 KB (+8,368 B (+13.1%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-funroll-all-loops' raises image text+data+bss by 8,368 B (13.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Unrolls even loops with unknown trip counts, adding remainder loops as well. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+8,368 B (+13.1%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-09 -- -finline-limit=1000  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-finline-limit=1000'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-finline-limit=1000' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 65.5 KB (+3,308 B (+5.2%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 10.7 KB (+3,664 B (+50.1%), INCREASES)
- **Meaning:** '-finline-limit=1000' raises stack high-water by 3,664 B (50.1%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Raises the inlining budget, so callee bodies are copied into every call site. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+3,308 B (+5.2%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-10 -- -fno-inline  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-inline'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-inline' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.8 KB (+532 B (+0.8%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,392 B (+80 B (+1.1%), NEUTRAL)
- **Meaning:** '-fno-inline' raises image text+data+bss by 532 B (0.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Disables inlining: calls replace copies. Note the catch: small static inline helpers (s_to_c, c_to_s) then become out-of-line copies in every translation unit, so code can even grow. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+532 B (+0.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-11 -- -ftree-vectorize -fvect-cost-model=dynamic  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-ftree-vectorize -fvect-cost-model=dynamic'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ftree-vectorize -fvect-cost-model=dynamic' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 63.4 KB (+1,140 B (+1.8%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ftree-vectorize -fvect-cost-model=dynamic' raises image text+data+bss by 1,140 B (1.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. O3-style vectorisation: SIMD body plus scalar prologue/epilogue and runtime alias checks. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+1,140 B (+1.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-12 -- -fipa-cp-clone  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fipa-cp-clone'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fipa-cp-clone' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Clones functions specialised for constant arguments, trading code size for speed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-13 -- -ffunction-sections -fdata-sections -Wl,--gc-sections  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-ffunction-sections -fdata-sections -Wl,--gc-sections'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffunction-sections -fdata-sections -Wl,--gc-sections' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 60.2 KB (-2,163 B (-3.4%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-ffunction-sections -fdata-sections -Wl,--gc-sections' lowers image text+data+bss by 2,163 B (3.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Each function/object in its own section lets the linker discard unreferenced ones. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,163 B (-3.4%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-14 -- -flto  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-flto'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-flto' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 59.5 KB (-2,855 B (-4.5%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,296 B (-16 B (-0.2%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 2,855 B (4.5%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Link-time optimisation sees the whole program: removes dead code and specialises across units. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-2,855 B (-4.5%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-15 -- -fno-asynchronous-unwind-tables -fno-unwind-tables  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-asynchronous-unwind-tables -fno-unwind-tables'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-asynchronous-unwind-tables -fno-unwind-tables' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 60.5 KB (-1,812 B (-2.8%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-asynchronous-unwind-tables -fno-unwind-tables' lowers image text+data+bss by 1,812 B (2.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Drops .eh_frame unwind tables; C code without exceptions does not need them to run. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-1,812 B (-2.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-16 -- -fmerge-all-constants  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fmerge-all-constants'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fmerge-all-constants' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Merges identical constants and arrays across the program; few duplicates exist here. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-17 -- -fshort-enums  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fshort-enums'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fshort-enums' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Enums take the smallest integer type; no bulk data here is enum-typed. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-18 -- -fno-plt  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-plt'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-plt' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.9 KB (+576 B (+0.9%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-fno-plt' raises image text+data+bss by 576 B (0.9%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Calls shared-library functions through the GOT instead of PLT stubs; tiny, mixed effect. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+576 B (+0.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-19 -- -fno-pie -no-pie  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-pie -no-pie'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-pie -no-pie' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 61.9 KB (-433 B (-0.7%), REDUCES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,136 B (-176 B (-2.4%), REDUCES)
- **Meaning:** '-fno-pie -no-pie' lowers stack high-water by 176 B (2.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Position-dependent executables need fewer dynamic relocations and GOT entries. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (-433 B (-0.7%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-20 -- -static  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-static'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-static' change resident memory, image size or stack depth?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 4,144 KB -> 3,088 KB (-1,056 KB (-25.5%), REDUCES); image text+data+bss: 62.3 KB -> 620.2 KB (+557.9 KB (+895.4%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 1,056 KB (25.5%) versus '-O2 (baseline)'. Static linking pulls libc into the image (image grows) but avoids mapping the shared libc, the loader and relocation of a single process (resident shrinks). Shared libraries only pay off when many processes share them. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+557.9 KB (+895.4%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+557.9 KB (+895.4%)).

### F-COM-21 -- -s  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-s'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-s' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Strips the symbol table: smaller file on disk, but symbols are never loaded, so RAM is unchanged. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-22 -- -g  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-g'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-g' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Debug info lives in non-allocated sections: the file grows, the resident image does not. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-23 -- -fstack-protector-all  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fstack-protector-all'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-all' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 65.2 KB (+3,009 B (+4.7%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,480 B (+168 B (+2.3%), INCREASES)
- **Meaning:** '-fstack-protector-all' raises stack high-water by 168 B (2.3%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. A canary slot and check sequence in every function: slightly larger frames and code. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+3,009 B (+4.7%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-24 -- -fstack-protector-strong  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fstack-protector-strong'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-protector-strong' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.9 KB (+597 B (+0.9%), INCREASES); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,480 B (+168 B (+2.3%), INCREASES)
- **Meaning:** '-fstack-protector-strong' raises stack high-water by 168 B (2.3%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Canaries only in functions with local arrays or address-taken locals. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+597 B (+0.9%)) is paid in full in flash/RAM, which Linux demand paging hides.

### F-COM-25 -- -fstack-clash-protection  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fstack-clash-protection'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fstack-clash-protection' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Probes each page of large stack allocations; adds code only where frames are large. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-26 -- -D_FORTIFY_SOURCE=2  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-D_FORTIFY_SOURCE=2'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-D_FORTIFY_SOURCE=2' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 4,144 KB -> 4,656 KB (+512 KB (+12.4%), INCREASES); image text+data+bss: 62.3 KB -> 62.4 KB (+83 B (+0.1%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-D_FORTIFY_SOURCE=2' raises max RSS (time -v) by 512 KB (12.4%) versus '-O2 (baseline)'. Bounds-checked variants of memcpy/strcpy etc. where sizes are known; a few extra bytes. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-27 -- -fno-omit-frame-pointer  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-omit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-omit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Keeps a frame pointer: one register lost and a save/restore per frame. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (INCREASES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-28 -- -fomit-frame-pointer  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fomit-frame-pointer'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fomit-frame-pointer' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.1 KB (-184 B (-0.3%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,120 B (-192 B (-2.6%), REDUCES)
- **Meaning:** '-fomit-frame-pointer' lowers stack high-water by 192 B (2.6%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Already enabled at -O1 and above on these targets; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-COM-29 -- -fno-optimize-sibling-calls  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-optimize-sibling-calls'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-optimize-sibling-calls' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (+40 B (+0.1%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 63.1 KB (+55.9 KB (+783.4%), INCREASES)
- **Meaning:** '-fno-optimize-sibling-calls' raises stack high-water by 55.9 KB (783.4%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Disables tail-call elimination: the recursive forecast keeps one frame per step instead of becoming a loop. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-30 -- -mcpu=native  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-mcpu=native'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-mcpu=native' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (-40 B (-0.1%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Tunes instruction selection for this exact CPU; code size and data size barely change. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-31 -- -ffast-math  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-ffast-math'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-ffast-math' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.2 KB (-122 B (-0.2%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,296 B (-16 B (-0.2%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Relaxes IEEE rules; memory-neutral, but it may change numerical results (watch the checksum). Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-32 -- -fvisibility=hidden  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fvisibility=hidden'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fvisibility=hidden' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Hides symbols from the dynamic table; executables export very little anyway. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-33 -- -fPIC  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fPIC'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fPIC' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.2 KB (-160 B (-0.3%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Library-style position independence in an executable: GOT-relative addressing, similar size. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-34 -- -fno-common  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fno-common'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fno-common' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). Default since GCC 10; included as a check that it is a no-op. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-35 -- -pipe  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-pipe'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-pipe' change resident memory, image size or stack depth?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). NEGATIVE CONTROL: -pipe only changes how the compiler passes temporary files. Any 'change' here is measurement noise, which validates the noise threshold. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### F-COM-36 -- -fsanitize=address  [compute]

- **Test:** Build the compute unit (HVAC prediction) at -O2 and again with '-fsanitize=address'; run each 10x at N=20,000 under time -v; read image sizes with size(1) and the stack high-water mark from a probe build.
- **Testing:** Does '-fsanitize=address' change resident memory, image size or stack depth?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 4,144 KB -> 11.1 MB (+7,232 KB (+174.5%), INCREASES); image text+data+bss: 62.3 KB -> 81.5 KB (+19.2 KB (+30.8%), INCREASES); tracked heap peak: 2.78 MB -> 2.75 MB (-36.5 KB (-1.3%), REDUCES)
- **Meaning:** '-fsanitize=address' raises max RSS (time -v) by 7,232 KB (174.5%) versus '-O2 (baseline)'. AddressSanitizer: shadow memory (1/8 of address space reserved), redzones around every allocation and a quarantine of freed blocks. A debugging tool, never a shipping config. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB. On an MMU-less microcontroller the image change (+19.2 KB (+30.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: tracked heap peak REDUCES (-36.5 KB (-1.3%)).

### F-LARGE-01 -- -O0 at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O0' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 103.8 KB (+4,016 B (+3.9%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O0' raises image text+data+bss by 4,016 B (3.9%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+4,016 B (+3.9%)) is paid in full in flash/RAM, which Linux demand paging hides. Run time changed +62% (0.320 s -> 0.520 s): a memory/time trade-off to weigh, not ignore. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-02 -- -Os at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-Os' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 98.6 KB (-1,256 B (-1.2%), REDUCES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-Os' lowers image text+data+bss by 1,256 B (1.2%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-1,256 B (-1.2%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-03 -- -O3 at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-O3' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 101.6 KB (+1,772 B (+1.7%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-O3' raises image text+data+bss by 1,772 B (1.7%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+1,772 B (+1.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-04 -- -flto at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-flto' still matter?
- **Hypothesis:** NEUTRAL
- **Outcome:** REDUCES (image only) -- max RSS (time -v): 31.5 MB -> 31.5 MB (-16 KB (-0.0%), NEUTRAL); image text+data+bss: 99.8 KB -> 97.0 KB (-2,903 B (-2.8%), REDUCES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-flto' lowers image text+data+bss by 2,903 B (2.8%) versus '-O2 (baseline)'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Compiler flags act on code (tens of KB); at this N the heap holds tens of MB, so even a real code-size change is a rounding error in resident memory. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (-2,903 B (-2.8%)) is paid in full in flash/RAM, which Linux demand paging hides. Hypothesis (NEUTRAL) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### F-LARGE-05 -- -static at production volume [mem]

- **Test:** Same comparison as the small-N flag tests, but the memory unit processes N=1,000,000 samples (data-dominated regime).
- **Testing:** Once data dominate the footprint, does '-static' still matter?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 30.9 MB (-656 KB (-2.0%), REDUCES); image text+data+bss: 99.8 KB -> 669.0 KB (+569.1 KB (+570.0%), INCREASES); tracked heap peak: 30.57 MB -> 30.57 MB (0 B (+0.0%), NEUTRAL)
- **Meaning:** '-static' lowers max RSS (time -v) by 656 KB (2.0%) versus '-O2 (baseline)'. Static linking removes a FIXED cost (shared libc mapping, loader, relocations), so it saves about the same absolute amount at any N -- a shrinking percentage as data grow. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 2.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+569.1 KB (+570.0%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+569.1 KB (+570.0%)).

### D-01 -- Sample type double -> float [io]

- **Test:** Recompile the I/O unit with CRITTER_SAMPLE_TYPE=float; same N, same naive record layout.
- **Testing:** How much of the acquisition buffer is the temperature representation?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 16.5 MB (-7,680 KB (-31.2%), REDUCES); image text+data+bss: 20.7 KB -> 20.7 KB (-40 B (-0.2%), NEUTRAL); tracked heap peak: 24.02 MB -> 16.02 MB (-8.00 MB (-33.3%), REDUCES)
- **Meaning:** 'float' lowers max RSS (time -v) by 7,680 KB (31.2%) versus 'double'. The naive record shrinks from 24 to 16 bytes; float still resolves 0.001 C. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 31.2% of what the Critter must provision.

### D-02 -- Sample type double -> fixed16 [io]

- **Test:** Recompile the I/O unit with CRITTER_SAMPLE_TYPE=fixed16 (int16 centi-degrees C).
- **Testing:** Can a fixed-point representation sized to the sensor's real resolution shrink the buffer?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 12.5 MB (-11.5 MB (-47.8%), REDUCES); image text+data+bss: 20.7 KB -> 21.0 KB (+264 B (+1.2%), INCREASES); tracked heap peak: 24.02 MB -> 12.02 MB (-12.00 MB (-50.0%), REDUCES)
- **Meaning:** 'fixed16' lowers max RSS (time -v) by 11.5 MB (47.8%) versus 'double'. A machine-room sensor resolves ~0.01-0.1 C over -40..125 C: 2 bytes are enough. The record drops to 12 bytes (half of the double version). At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 47.8% of what the Critter must provision. On an MMU-less microcontroller the image change (+264 B (+1.2%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+264 B (+1.2%)). Run time changed +33% (0.030 s -> 0.040 s): a memory/time trade-off to weigh, not ignore.

### D-03 -- Record layout naive -> reordered [io]

- **Test:** Recompile with CRITTER_LAYOUT=1: identical fields, ordered largest-alignment first.
- **Testing:** How much memory is wasted in struct padding?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 16.5 MB (-7,680 KB (-31.2%), REDUCES); image text+data+bss: 20.7 KB -> 20.5 KB (-168 B (-0.8%), REDUCES); tracked heap peak: 24.02 MB -> 16.02 MB (-8.00 MB (-33.3%), REDUCES)
- **Meaning:** 'reordered' lowers max RSS (time -v) by 7,680 KB (31.2%) versus 'naive'. {u8, double, u8, u32} has 7+3 bytes of padding holes (24 B); {double, u32, u8, u8} needs only 2 bytes of tail padding (16 B). Zero cost. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 31.2% of what the Critter must provision. On an MMU-less microcontroller the image change (-168 B (-0.8%)) is paid in full in flash/RAM, which Linux demand paging hides.

### D-04 -- Record layout naive -> packed [io]

- **Test:** Recompile with CRITTER_LAYOUT=2: __attribute__((packed)) on the naive order.
- **Testing:** Does removing all padding beat reordering, and what does it cost?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 14.5 MB (-9,728 KB (-39.5%), REDUCES); image text+data+bss: 20.7 KB -> 20.8 KB (+40 B (+0.2%), NEUTRAL); tracked heap peak: 24.02 MB -> 14.02 MB (-10.00 MB (-41.6%), REDUCES)
- **Meaning:** 'packed' lowers max RSS (time -v) by 9,728 KB (39.5%) versus 'naive'. Packed records are 14 B (vs 16 B reordered) but force unaligned loads; on Cortex-A76 these are legal but slower, and on Cortex-M0 they fault. Reordering gets most of the gain for free. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 39.5% of what the Critter must provision.

### D-05 -- Sample type double -> float [mem]

- **Test:** Recompile the memory unit (copy_sort) with float samples.
- **Testing:** Does halving the element size halve the outlier-removal footprint?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 23.9 MB (-7,808 KB (-24.2%), REDUCES); image text+data+bss: 99.8 KB -> 99.9 KB (+104 B (+0.1%), NEUTRAL); tracked heap peak: 30.57 MB -> 19.14 MB (-11.43 MB (-37.4%), REDUCES)
- **Meaning:** 'float' lowers max RSS (time -v) by 7,808 KB (24.2%) versus 'double'. Only 3 of the 4 N-sized buffers shrink: the junior-dev code always builds a double deviation array. The type of the dominant buffer is what matters. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 24.2% of what the Critter must provision.

### D-06 -- Sample type double -> fixed16 [mem]

- **Test:** Recompile the memory unit (copy_sort) with int16 fixed-point samples.
- **Testing:** How far can representation alone go for the memory unit?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 20.1 MB (-11.4 MB (-36.3%), REDUCES); image text+data+bss: 99.8 KB -> 100.2 KB (+376 B (+0.4%), NEUTRAL); tracked heap peak: 30.57 MB -> 13.42 MB (-17.15 MB (-56.1%), REDUCES)
- **Meaning:** 'fixed16' lowers max RSS (time -v) by 11.4 MB (36.3%) versus 'double'. Raw, sorted and cleaned copies drop to 2 B/sample; the double deviation array stays 8 B. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 36.3% of what the Critter must provision.

### D-07 -- Input type double -> fixed16 [compute]

- **Test:** Recompile the compute unit (materialized fit) with int16 input samples.
- **Testing:** Does shrinking the input help when the working set is a derived matrix?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 138.5 MB -> 132.5 MB (-6,144 KB (-4.3%), REDUCES); image text+data+bss: 62.3 KB -> 62.6 KB (+336 B (+0.5%), INCREASES); tracked heap peak: 137.37 MB -> 131.66 MB (-5.72 MB (-4.2%), REDUCES)
- **Meaning:** 'fixed16' lowers max RSS (time -v) by 6,144 KB (4.3%) versus 'double'. The design matrix X and its transpose are 2 x N x p doubles (128 B/sample at p=8); the input is 8 B/sample. Shrinking the input barely dents the total: optimise the dominant buffer first. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 4.3% of what the Critter must provision. On an MMU-less microcontroller the image change (+336 B (+0.5%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: image text+data+bss INCREASES (+336 B (+0.5%)).

### A-01 -- Growable vector -> exact heap allocation [io]

- **Test:** Run the I/O unit with --strategy=heap (one malloc of N records) instead of realloc doubling.
- **Testing:** What does not knowing the size in advance cost?
- **Hypothesis:** REDUCES
- **Outcome:** NEUTRAL -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 24.02 MB -> 22.89 MB (-1.12 MB (-4.7%), REDUCES)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-123 KB). Doubling rounds capacity up to the next power of two and realloc may briefly hold old and new blocks. Compare tracked heap (bytes reserved) with max RSS (pages touched): on Linux the unused tail of a large mmap'd block is never touched, and glibc grows big blocks with mremap instead of copying, so the waste is address space, not RAM. On an MCU heap the same tail is real, unusable RAM. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### A-02 -- Growable vector -> static .bss buffer [io]

- **Test:** Rebuild with -DCRITTER_IO_STATIC_CAP=1000000 and run --strategy=static.
- **Testing:** Heap vs. statically reserved buffer: resident cost and image cost.
- **Hypothesis:** REDUCES
- **Outcome:** INCREASES (image only) -- max RSS (time -v): 24.0 MB -> 24.0 MB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 20.7 KB -> 22.91 MB (+22.89 MB (+113154.7%), INCREASES); tracked heap peak: 24.02 MB -> 0 B (-24.02 MB (-100.0%), REDUCES)
- **Meaning:** 'static' raises image text+data+bss by 22.89 MB (113154.7%) versus 'grow'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Resident cost equals the exact-heap case (pages are touched the same way) but the buffer moves into .bss: the image grows by N x record size. On an MCU that is RAM reserved at link time, which is exactly what makes worst-case usage provable. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 0.0% of what the Critter must provision. On an MMU-less microcontroller the image change (+22.89 MB (+113154.7%)) is paid in full in flash/RAM, which Linux demand paging hides. Trade-off: tracked heap peak REDUCES (-24.02 MB (-100.0%)). Hypothesis (REDUCES) refuted: worth a closer look in the report (check the image breakdown in builds.log and the phase snapshots in phases.csv).

### A-03 -- Store-everything -> bounded ring buffer [io]

- **Test:** Run the I/O unit with --strategy=ring: keep only the current W=1000-record window.
- **Testing:** Does the I/O unit need to retain the raw stream at all?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 24.0 MB -> 1,088 KB (-23.0 MB (-95.6%), REDUCES); image text+data+bss: 20.7 KB -> 20.7 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 24.02 MB -> 23.4 KB (-23.99 MB (-99.9%), REDUCES)
- **Meaning:** 'ring' lowers max RSS (time -v) by 23.0 MB (95.6%) versus 'grow'. Summaries are computed as each window fills, so memory is O(W) instead of O(N) and the output is bit-identical. This is the single most important embedded pattern: bounded buffers make memory independent of uptime. At N=1,000,000 the baseline needs 24.0 MB resident, so the change is 95.6% of what the Critter must provision.

### A-04 -- Allocator policy: mmap threshold raised [pipeline/phased]

- **Test:** Run the phased pipeline with GLIBC_TUNABLES=glibc.malloc.mmap_threshold=33554432 so that blocks up to 32 MB come from the brk heap instead of mmap.
- **Testing:** Does freeing memory actually give it back to the OS?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (resident) -- max RSS (time -v): 138.4 MB -> 146.0 MB (+7,840 KB (+5.5%), INCREASES); image text+data+bss: 24.9 KB -> 24.9 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 137.23 MB -> 137.22 MB (-11.5 KB (-0.0%), NEUTRAL)
- **Meaning:** 'mmap_threshold=32MB' raises max RSS (time -v) by 7,840 KB (5.5%) versus 'default malloc'. mmap'd blocks are unmapped on free(); brk-heap blocks are only returned if they sit at the top of the heap. 'Phased' code relies on free() releasing memory, so the allocator policy decides whether phasing works. At N=1,000,000 the baseline needs 138.4 MB resident, so the change is 5.5% of what the Critter must provision.

### G-01 -- copy+qsort -> quickselect in place [mem]

- **Test:** Run the memory unit with --strategy=inplace (one scratch copy, quickselect, in-place compaction).
- **Testing:** How much of the junior-dev footprint is avoidable copying?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 16.5 MB (-15.0 MB (-47.5%), REDUCES); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 30.57 MB -> 15.28 MB (-15.29 MB (-50.0%), REDUCES)
- **Meaning:** 'inplace' lowers max RSS (time -v) by 15.0 MB (47.5%) versus 'copy_sort'. Four N-sized buffers become two, and the scratch is freed before summarising. Results are identical. Also compare RSS with tracked heap: glibc's qsort may malloc a hidden temporary the size of the array (merge sort), memory the program never asked for. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 47.5% of what the Critter must provision. Run time changed -84% (0.320 s -> 0.050 s): a memory/time trade-off to weigh, not ignore.

### G-02 -- copy+qsort -> fixed histogram [mem]

- **Test:** Run --strategy=histogram: median and MAD from a 20001-bin (80 KB) histogram, no copy.
- **Testing:** Can sensor-domain knowledge replace a data-sized buffer with a fixed one?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 8,752 KB (-23.0 MB (-72.9%), REDUCES); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 30.57 MB -> 7.67 MB (-22.90 MB (-74.9%), REDUCES)
- **Meaning:** 'histogram' lowers max RSS (time -v) by 23.0 MB (72.9%) versus 'copy_sort'. The sensor's range and resolution are known, so a counting histogram gives the median in O(1) extra memory (quantised to 0.01 C, which is the sensor's resolution anyway). At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 72.9% of what the Critter must provision. Run time changed -88% (0.320 s -> 0.040 s): a memory/time trade-off to weigh, not ignore.

### G-03 -- batch -> streaming windows [mem]

- **Test:** Run --strategy=streaming: robust filtering per W=1000 window; the full stream is never stored.
- **Testing:** What is the floor for the memory unit if data are processed as they arrive?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 31.5 MB -> 1,072 KB (-30.5 MB (-96.7%), REDUCES); image text+data+bss: 99.8 KB -> 99.8 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 30.57 MB -> 46.9 KB (-30.52 MB (-99.9%), REDUCES)
- **Meaning:** 'streaming' lowers max RSS (time -v) by 30.5 MB (96.7%) versus 'copy_sort'. Memory is O(W), independent of N. The statistic becomes local (per-window median), which tracks HVAC drift better but is a design decision, not a free optimisation. At N=1,000,000 the baseline needs 31.5 MB resident, so the change is 96.7% of what the Critter must provision. Run time changed -84% (0.320 s -> 0.050 s): a memory/time trade-off to weigh, not ignore.

### G-04 -- materialized matrix -> streaming normal equations [compute]

- **Test:** Run the compute unit with --mode=streaming: accumulate XtX and Xty sample by sample.
- **Testing:** Does the prediction need the design matrix at all?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 138.5 MB -> 1,088 KB (-137.5 MB (-99.2%), REDUCES); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 137.37 MB -> 40.3 KB (-137.34 MB (-100.0%), REDUCES)
- **Meaning:** 'streaming' lowers max RSS (time -v) by 137.5 MB (99.2%) versus 'materialized'. Least squares only needs XtX (p x p) and Xty (p). Materialising X and an explicit transpose costs 2 x N x p doubles; streaming costs p^2 doubles. Identical coefficients. At N=1,000,000 the baseline needs 138.5 MB resident, so the change is 99.2% of what the Critter must provision. Run time changed -71% (0.420 s -> 0.120 s): a memory/time trade-off to weigh, not ignore.

### O-01 -- All buffers live -> free when dead (phased)

- **Test:** Run the full pipeline with --mode=phased: each phase frees its buffers before the next starts.
- **Testing:** Is peak memory the sum of the phases or the maximum phase?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 153.5 MB -> 138.4 MB (-15.2 MB (-9.9%), REDUCES); image text+data+bss: 24.9 KB -> 24.9 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 152.66 MB -> 137.23 MB (-15.43 MB (-10.1%), REDUCES)
- **Meaning:** 'phased' lowers max RSS (time -v) by 15.2 MB (9.9%) versus 'concurrent'. Concurrent peak = SUM of all buffers; phased peak = MAX over phases. The saving is bounded by the phases that are not the largest one. At N=1,000,000 the baseline needs 153.5 MB resident, so the change is 9.9% of what the Critter must provision.

### O-02 -- All buffers live -> data overlay arena

- **Test:** Run --mode=overlay: one arena sized for the largest phase; cleaned data overlay the raw data and the design matrix overlays the cleaning scratch.
- **Testing:** Does a classic overlay scheme (applied to data) reduce peak memory?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 153.5 MB -> 138.0 MB (-15.5 MB (-10.1%), REDUCES); image text+data+bss: 24.9 KB -> 24.9 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 152.66 MB -> 137.34 MB (-15.31 MB (-10.0%), REDUCES)
- **Meaning:** 'overlay' lowers max RSS (time -v) by 15.5 MB (10.1%) versus 'concurrent'. An overlay plan fixes the peak at compile/plan time: raw + max(scratch, design matrix). No allocator, no fragmentation, and the worst case is known before deployment. At N=1,000,000 the baseline needs 153.5 MB resident, so the change is 10.1% of what the Critter must provision.

### O-03 -- Phased (allocator) -> overlay (planned)

- **Test:** Compare --mode=phased with --mode=overlay directly.
- **Testing:** Is there any resident difference between letting malloc reuse memory and planning reuse?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 138.4 MB -> 138.0 MB (-352 KB (-0.2%), NEUTRAL); image text+data+bss: 24.9 KB -> 24.9 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 137.23 MB -> 137.34 MB (+115.7 KB (+0.1%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-709 KB). Both reach peak = largest phase. The overlay's value is determinism (no heap churn, no fragmentation over months of uptime), not a smaller peak. At N=1,000,000 the baseline needs 138.4 MB resident, so the change is 0.2% of what the Critter must provision.

### O-04 -- Overlay + streaming fit (shrink the dominant phase)

- **Test:** Run --mode=overlay --fit=streaming against the concurrent junior-dev pipeline.
- **Testing:** Combine the overlay with removing the largest phase's buffers.
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 153.5 MB -> 16.0 MB (-137.5 MB (-89.5%), REDUCES); image text+data+bss: 24.9 KB -> 24.9 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 152.66 MB -> 15.27 MB (-137.39 MB (-90.0%), REDUCES)
- **Meaning:** 'overlay+streaming' lowers max RSS (time -v) by 137.5 MB (89.5%) versus 'concurrent'. Overlays can only reduce peak to the largest phase; to go lower you must shrink that phase. With the design matrix gone the peak falls to raw + scratch. At N=1,000,000 the baseline needs 153.5 MB resident, so the change is 89.5% of what the Critter must provision. Run time changed -72% (0.430 s -> 0.120 s): a memory/time trade-off to weigh, not ignore.

### O-05 -- Single process -> one process per phase (exec overlay)

- **Test:** Run acquire, clean and predict as three separate processes that hand data off through a file; peak = the largest of the three max RSS values.
- **Testing:** Does splitting the pipeline into processes (the OS version of an overlay) lower the peak?
- **Hypothesis:** REDUCES
- **Outcome:** REDUCES (resident) -- max RSS (time -v): 153.5 MB -> 138.0 MB (-15.5 MB (-10.1%), REDUCES)
- **Meaning:** 'one process per phase' lowers max RSS (time -v) by 15.5 MB (10.1%) versus 'concurrent'. Each process starts with an empty heap and returns everything at exit, so peak is the largest stage; the cost is file I/O and one process floor per stage. At N=1,000,000 the baseline needs 153.5 MB resident, so the change is 10.1% of what the Critter must provision.

### S-01 -- Solver workspace heap -> stack [compute]

- **Test:** Run the compute unit with --scratch=stack: the 8 KB system + 32 KB trajectory become locals.
- **Testing:** Where does moving a buffer from heap to stack show up?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 47.4 KB (+40.3 KB (+563.9%), INCREASES)
- **Meaning:** 'scratch=stack' raises stack high-water by 40.3 KB (563.9%) versus 'scratch=heap'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. The bytes merely move: heap shrinks, stack grows by ~40 KB. With an 8 MB default stack this is invisible on Linux; on an RTOS task with a 4 KB stack it is a crash. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### S-02 -- Solver workspace heap -> static [compute]

- **Test:** Run with --scratch=static: the workspace is a .bss array.
- **Testing:** Static allocation: what moves to the image, what leaves the heap?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). The .bss array is in every compute build, so resident memory is the same; static placement makes the requirement visible to the linker and removes a failure path. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### S-03 -- Scenario tree depth 10 -> 14 [compute]

- **Test:** Increase the recursive scenario tree depth from 10 to 14.
- **Testing:** Does data-dependent recursion depth drive stack usage?
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 9,744 B (+2,432 B (+33.3%), INCREASES)
- **Meaning:** 'depth=14' raises stack high-water by 2,432 B (33.3%) versus 'depth=10'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Each level keeps two local history arrays (~0.5 KB) alive; stack grows linearly with depth while run time grows 16x. Unbounded recursion has no place in firmware. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### S-04 -- Tail-recursive horizon 1000 -> 4000 at -O2 [compute]

- **Test:** Quadruple the recursive forecast horizon with tail-call optimisation enabled (-O2).
- **Testing:** Does recursion depth cost stack when the compiler turns tail calls into loops?
- **Hypothesis:** NEUTRAL
- **Outcome:** NEUTRAL -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 62.3 KB -> 62.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 7,312 B -> 7,312 B (0 B (+0.0%), NEUTRAL)
- **Meaning:** No memory dimension moved beyond measurement noise (RSS threshold +/-32 KB). At -O2 the tail call becomes a jump: stack is constant in the horizon. The same source at -O0 uses one frame per step (see S-05) -- the stack bound depends on the build flags, so it must be verified for the shipping configuration. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### S-05 -- Tail-recursive horizon 1000 -> 4000 at -O0 [compute]

- **Test:** Same horizons as S-04 but built at -O0 (no tail-call elimination).
- **Testing:** Recursion depth without the compiler's help.
- **Hypothesis:** INCREASES
- **Outcome:** INCREASES (stack only) -- max RSS (time -v): 4,144 KB -> 4,144 KB (0 KB (+0.0%), NEUTRAL); image text+data+bss: 66.3 KB -> 66.3 KB (0 B (+0.0%), NEUTRAL); tracked heap peak: 2.78 MB -> 2.78 MB (0 B (+0.0%), NEUTRAL); stack high-water: 78.9 KB -> 313.2 KB (+234.4 KB (+297.1%), INCREASES)
- **Meaning:** 'horizon=4000 -O0' raises stack high-water by 234.4 KB (297.1%) versus 'horizon=1000 -O0'. Resident memory on Linux did not move measurably because demand paging only charges pages that are touched and RSS is counted in whole pages. Without sibling-call optimisation every step keeps a frame: stack grows linearly. Measured at N=20,000 (code/runtime-dominated), this bounds what the lever can ever save; the process floor alone is 1,088 KB.

### S-06 -- Fits in a 128 KB stack? [compute]

- **Test:** Run builds of the compute unit with the stack rlimit set to 128 KB (ulimit -s), emulating a small RTOS task stack.
- **Testing:** Which build configurations survive a small fixed stack?
- **Outcome:** PASS: -O2, -O2 -fno-optimize-sibling-calls, -Os, -O2 scratch=stack   |   FAIL: -O0
- **Meaning:** Of 5 configurations, 4 fit the limit. A SIGSEGV here is a stack overflow. The same source passes or fails depending on the optimisation flags: stack budgets must be proven per build configuration.

### C-01 -- I/O unit: store-everything vs ring buffer

- **Test:** Run each configuration at N = 125,000, 250,000, 500,000, 1,000,000 and fit maxRSS = floor + slope x N.
- **Testing:** How does memory grow with the amount of data (i.e. with uptime between uploads)?
- **Outcome:** grow: O(N): 23.9 B/sample; a 64 MB budget holds ~2,754,622 samples (~7.7 h at 100 Hz); ring: BOUNDED (memory independent of N)
- **Meaning:** 'grow' costs 23.9 bytes per sample retained, 'ring' 0.0 (effectively flat). The slope (bytes per sample) is the design's true memory cost. A slope near zero means memory is bounded and the device can run indefinitely; any positive slope is a maximum uptime before it runs out of RAM.

### C-02 -- Memory unit: copy_sort vs inplace vs streaming

- **Test:** Run each configuration at N = 125,000, 250,000, 500,000, 1,000,000 and fit maxRSS = floor + slope x N.
- **Testing:** How does memory grow with the amount of data (i.e. with uptime between uploads)?
- **Outcome:** copy_sort: O(N): 32.1 B/sample; a 64 MB budget holds ~2,056,544 samples (~5.7 h at 100 Hz); inplace: O(N): 16.1 B/sample; a 64 MB budget holds ~4,091,974 samples (~11.4 h at 100 Hz); streaming: BOUNDED (memory independent of N)
- **Meaning:** 'copy_sort' costs 32.1 bytes per sample retained, 'streaming' 0.0 (effectively flat). The slope (bytes per sample) is the design's true memory cost. A slope near zero means memory is bounded and the device can run indefinitely; any positive slope is a maximum uptime before it runs out of RAM.

### C-03 -- Compute unit: materialized vs streaming fit

- **Test:** Run each configuration at N = 125,000, 250,000, 500,000, 1,000,000 and fit maxRSS = floor + slope x N.
- **Testing:** How does memory grow with the amount of data (i.e. with uptime between uploads)?
- **Outcome:** materialized: O(N): 144.2 B/sample; a 64 MB budget holds ~458,414 samples (~1.3 h at 100 Hz); streaming: BOUNDED (memory independent of N)
- **Meaning:** 'materialized' costs 144.2 bytes per sample retained, 'streaming' 0.0 (effectively flat). The slope (bytes per sample) is the design's true memory cost. A slope near zero means memory is bounded and the device can run indefinitely; any positive slope is a maximum uptime before it runs out of RAM.

### C-04 -- Pipeline: junior-dev vs overlay+streaming

- **Test:** Run each configuration at N = 125,000, 250,000, 500,000, 1,000,000 and fit maxRSS = floor + slope x N.
- **Testing:** How does memory grow with the amount of data (i.e. with uptime between uploads)?
- **Outcome:** concurrent: O(N): 160.0 B/sample; a 64 MB budget holds ~412,751 samples (~1.1 h at 100 Hz); overlay+streaming: O(N): 15.5 B/sample; a 64 MB budget holds ~4,245,358 samples (~11.8 h at 100 Hz)
- **Meaning:** 'concurrent' costs 160.0 bytes per sample retained, 'overlay+streaming' 15.5 (10x less). The slope (bytes per sample) is the design's true memory cost. A slope near zero means memory is bounded and the device can run indefinitely; any positive slope is a maximum uptime before it runs out of RAM.

### B-01 -- Which pipeline fits a 64 MB device?

- **Test:** Run each pipeline memory plan with the address-space rlimit set to 64 MB (N=1,000,000), emulating a small embedded Linux target.
- **Testing:** Pass/fail under a hard memory budget, the way the product would actually fail.
- **Outcome:** PASS: phased/streaming, overlay/streaming   |   FAIL: concurrent/materialized, phased/materialized, overlay/materialized
- **Meaning:** Of 5 configurations, 2 fit the limit. RLIMIT_AS caps virtual address space, so malloc returns NULL exactly as on a device without swap. A configuration either fits or it does not; there is no 'mostly fits' in an unattended machine room.

