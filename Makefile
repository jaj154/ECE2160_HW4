# Convenience builds for manual experiments.  The harness (run_memlab.py)
# does its own builds with per-test flags; this Makefile is for poking around.
#   make            build all units at -O2
#   make CFLAGS_OPT="-Os -flto"   try other flags
#   make probe      stack-probe builds (stack metric only, never RSS)
CC        ?= gcc
CFLAGS_OPT ?= -O2
CFLAGS    := -std=gnu11 -Wall -ffp-contract=off -Isrc $(CFLAGS_OPT)
COMMON    := src/critter_common.c src/critter_algo.c
BIN       := bin
UNITS     := io mem compute pipeline

all: $(addprefix $(BIN)/,$(UNITS) noop)

$(BIN):
	mkdir -p $(BIN)

$(BIN)/io: src/unit_io.c $(COMMON) | $(BIN)
	$(CC) $(CFLAGS) $^ -o $@ -lm
$(BIN)/mem: src/unit_mem.c $(COMMON) | $(BIN)
	$(CC) $(CFLAGS) $^ -o $@ -lm
$(BIN)/compute: src/unit_compute.c $(COMMON) | $(BIN)
	$(CC) $(CFLAGS) $^ -o $@ -lm
$(BIN)/pipeline: src/pipeline.c $(COMMON) | $(BIN)
	$(CC) $(CFLAGS) $^ -o $@ -lm
$(BIN)/noop: src/noop.c src/critter_common.c | $(BIN)
	$(CC) $(CFLAGS) $^ -o $@ -lm

probe: | $(BIN)
	$(CC) $(CFLAGS) -DCRITTER_STACK_PROBE src/unit_compute.c $(COMMON) -o $(BIN)/compute_probe -lm

clean:
	rm -rf $(BIN) build

.PHONY: all probe clean
