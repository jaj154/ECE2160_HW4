#!/usr/bin/env bash
# HW4 follow-up measurements requested by the grader. Run from the critter-memlab directory on the Pi 5:
#   bash hw4_followup.sh
# Produces followup_<timestamp>.zip, about 10-20 minutes. Upload that zip.
set -u
cd "$(dirname "$0")"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT="followup_$STAMP"
mkdir -p "$OUT/bin"
CF="-std=gnu11 -Wall -Wno-unused-function -ffp-contract=off -Isrc"
COMMON="src/critter_common.c src/critter_algo.c"
NOASLR="setarch $(uname -m) -R"
TIME=/usr/bin/time
[ -x "$TIME" ] || { echo "GNU time missing: sudo apt install time"; exit 1; }

echo "== 1/4 environment"
{ uname -a; getconf PAGESIZE; gcc --version | head -1; ldd --version | head -1; ld --version | head -1
  cat /proc/device-tree/model; echo; } > "$OUT/env.txt" 2>&1

echo "== 2/4 new flags on all units + production-volume flags on io and compute (harness)"
ONLY=""
for u in IO MEM COM; do for i in 37 38 39 40 41 42 43; do ONLY="$ONLY,F-$u-$i"; done; done
ONLY="${ONLY#,},F-LIO,F-LCOM,F-LARGE"
python3 run_memlab.py --suite flags --only "$ONLY" --repeats 10 --no-aslr --no-color --logdir "$OUT/logs" \
  | tee "$OUT/harness_console.txt"

echo "== 3/4 raw time -v excerpts (baselines, N=1,000,000)"
for u in io mem compute; do
  src=src/unit_$u.c
  gcc $CF -O2 "$src" $COMMON -o "$OUT/bin/${u}_O2" -lm
  $NOASLR $TIME -v "$OUT/bin/${u}_O2" --n=1000000 > "$OUT/stdout_${u}.txt" 2> "$OUT/timev_${u}.txt"
done

echo "== 4/4 FORTIFY investigation"
gcc $CF -O2 src/unit_io.c $COMMON -o "$OUT/bin/io_plain" -lm
gcc $CF -O2 -D_FORTIFY_SOURCE=2 src/unit_io.c $COMMON -o "$OUT/bin/io_fortify" -lm
gcc $CF -O2 src/noop.c src/critter_common.c -o "$OUT/bin/noop_plain" -lm
gcc $CF -O2 -D_FORTIFY_SOURCE=2 src/noop.c src/critter_common.c -o "$OUT/bin/noop_fortify" -lm
gcc -shared -fPIC -O2 tools/smapsdump.c -o "$OUT/bin/smapsdump.so"
ARGS="--strategy=grow --window=1000 --n=20000"
for b in io_plain io_fortify noop_plain noop_fortify; do
  a=""; [[ $b == io_* ]] && a="$ARGS"
  : > "$OUT/maxrss_$b.txt"
  for i in $(seq 10); do $NOASLR $TIME -f "%M" -o "$OUT/tmp.txt" "$OUT/bin/$b" $a > /dev/null; cat "$OUT/tmp.txt" >> "$OUT/maxrss_$b.txt"; done
  CRITTER_SMAPS_OUT="$OUT/smaps_$b.txt" LD_PRELOAD="$OUT/bin/smapsdump.so" $NOASLR "$OUT/bin/$b" $a > /dev/null
  readelf -lW "$OUT/bin/$b" > "$OUT/readelf_$b.txt"
  nm -D --undefined-only "$OUT/bin/$b" > "$OUT/imports_$b.txt" 2>&1
  if command -v strace > /dev/null; then
    $NOASLR strace -f -e trace=execve,openat,mmap,munmap,mprotect,brk,mremap -o "$OUT/strace_$b.txt" "$OUT/bin/$b" $a > /dev/null
  fi
done
rm -f "$OUT/tmp.txt"
command -v strace > /dev/null || echo "strace not installed (optional: sudo apt install strace)" | tee "$OUT/NOTE_strace.txt"

zip -qr "$OUT.zip" "$OUT" -x "$OUT/bin/*"
echo "Done: $OUT.zip"
