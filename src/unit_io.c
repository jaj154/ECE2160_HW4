/*
 * unit_io.c - Critter I/O unit.
 *
 * Reads temperature samples at a high rate (simulated 100 Hz) from up to
 * four sensors, stores them as records, and produces per-window summaries
 * for off-line analysis.  Every strategy produces the SAME summaries, so
 * the checksum doubles as a correctness check across strategies.
 *
 * Runtime knobs:
 *   --n=N               samples to acquire           (default 1000000)
 *   --window=W          samples per summary window   (default 1000)
 *   --strategy=grow     realloc-doubling vector (the junior-dev default)
 *              heap     one exact malloc(N)
 *              static   fixed .bss array (needs -DCRITTER_IO_STATIC_CAP=N)
 *              ring     bounded ring of W records, summarize as you go
 *
 * Compile-time knobs:
 *   -DCRITTER_LAYOUT=0  naive field order (padding holes)  [default]
 *                    1  fields ordered by alignment
 *                    2  __attribute__((packed))
 */
#include "critter_algo.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef CRITTER_LAYOUT
#define CRITTER_LAYOUT 0
#endif

#if CRITTER_LAYOUT == 0
#define LAYOUT_NAME "naive"
typedef struct {
    uint8_t  sensor_id;
    sample_t temp;
    uint8_t  status;
    uint32_t t_ms;
} record_t;
#elif CRITTER_LAYOUT == 1
#define LAYOUT_NAME "reordered"
#if CRITTER_SAMPLE_TYPE == CRITTER_T_FIXED16
typedef struct { uint32_t t_ms; sample_t temp; uint8_t sensor_id; uint8_t status; } record_t;
#else
typedef struct { sample_t temp; uint32_t t_ms; uint8_t sensor_id; uint8_t status; } record_t;
#endif
#elif CRITTER_LAYOUT == 2
#define LAYOUT_NAME "packed"
typedef struct __attribute__((packed)) {
    uint8_t  sensor_id;
    sample_t temp;
    uint8_t  status;
    uint32_t t_ms;
} record_t;
#else
#error "unknown CRITTER_LAYOUT"
#endif

#ifdef CRITTER_IO_STATIC_CAP
static record_t g_static_buf[CRITTER_IO_STATIC_CAP];
#endif

static record_t make_record(sensor_t *s, size_t i)
{
    record_t r;
    double   c  = sensor_read_c(s);
    r.sensor_id = (uint8_t)(i & 3u);
    r.temp      = c_to_s(c);
    r.status    = (uint8_t)(c > 40.0 || c < 0.0);
    r.t_ms      = (uint32_t)(i * 10u);
    return r;
}

/* window summary over records (same arithmetic order in every strategy) */
static void summarize_records(const record_t *r, size_t n, summary_t *out)
{
    double sum = 0.0, mn = 1e300, mx = -1e300;
    for (size_t i = 0; i < n; i++) {
        double c = s_to_c(r[i].temp);
        sum += c;
        if (c < mn) mn = c;
        if (c > mx) mx = c;
    }
    out->mean  = n ? sum / (double)n : 0.0;
    out->min   = n ? mn : 0.0;
    out->max   = n ? mx : 0.0;
    out->count = n;
}

static int64_t summarize_buffer(const record_t *buf, size_t n, size_t W)
{
    int64_t cs = 0;
    for (size_t i = 0; i < n; i += W) {
        summary_t s;
        size_t    len = (n - i < W) ? n - i : W;
        summarize_records(buf + i, len, &s);
        cs += summary_checksum(&s, 1);
    }
    return cs;
}

static int64_t run_grow(size_t n, size_t W)
{
    size_t    cap = 16, len = 0;
    record_t *buf = (record_t *)cm_malloc(cap * sizeof *buf);
    if (!buf) critter_oom("grow-initial", cap * sizeof *buf);
    sensor_t s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) {
        if (len == cap) {
            cap *= 2;
            record_t *nb = (record_t *)cm_realloc(buf, cap * sizeof *buf);
            if (!nb) critter_oom("grow-realloc", cap * sizeof *buf);
            buf = nb;
        }
        buf[len++] = make_record(&s, i);
    }
    printf("@@buffer_capacity=%zu\n", cap);
    critter_phase("acquire");
    int64_t cs = summarize_buffer(buf, len, W);
    critter_phase("summarize");
    cm_free(buf);
    return cs;
}

static int64_t run_heap(size_t n, size_t W)
{
    record_t *buf = (record_t *)cm_xmalloc(n * sizeof *buf, "heap-buffer");
    sensor_t  s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) buf[i] = make_record(&s, i);
    printf("@@buffer_capacity=%zu\n", n);
    critter_phase("acquire");
    int64_t cs = summarize_buffer(buf, n, W);
    critter_phase("summarize");
    cm_free(buf);
    return cs;
}

static int64_t run_static(size_t n, size_t W)
{
#ifdef CRITTER_IO_STATIC_CAP
    if (n > (size_t)CRITTER_IO_STATIC_CAP) {
        fprintf(stderr, "io: n=%zu exceeds CRITTER_IO_STATIC_CAP=%zu; clamping\n", n,
                (size_t)CRITTER_IO_STATIC_CAP);
        n = CRITTER_IO_STATIC_CAP;
    }
    sensor_t s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) g_static_buf[i] = make_record(&s, i);
    printf("@@buffer_capacity=%zu\n", (size_t)CRITTER_IO_STATIC_CAP);
    critter_phase("acquire");
    int64_t cs = summarize_buffer(g_static_buf, n, W);
    critter_phase("summarize");
    return cs;
#else
    (void)n;
    (void)W;
    fprintf(stderr, "io: strategy=static requires -DCRITTER_IO_STATIC_CAP=<records>\n");
    exit(2);
#endif
}

static int64_t run_ring(size_t n, size_t W)
{
    record_t *ring = (record_t *)cm_xmalloc(W * sizeof *ring, "ring-buffer");
    sensor_t  s;
    sensor_init(&s, 42);
    int64_t cs  = 0;
    size_t  len = 0;
    for (size_t i = 0; i < n; i++) {
        ring[len++] = make_record(&s, i);
        if (len == W) {
            summary_t sm;
            summarize_records(ring, len, &sm);
            cs += summary_checksum(&sm, 1);
            len = 0;
        }
    }
    if (len) {
        summary_t sm;
        summarize_records(ring, len, &sm);
        cs += summary_checksum(&sm, 1);
    }
    printf("@@buffer_capacity=%zu\n", W);
    critter_phase("acquire+summarize");
    cm_free(ring);
    return cs;
}

int main(int argc, char **argv)
{
    critter_begin("io");
    size_t      n     = (size_t)arg_long(argc, argv, "n", 1000000);
    size_t      W     = (size_t)arg_long(argc, argv, "window", 1000);
    const char *strat = arg_str(argc, argv, "strategy", "grow");
    if (W == 0) W = 1;

    printf("@@strategy=%s\n@@n=%zu\n@@window=%zu\n@@layout=%s\n@@record_bytes=%zu\n", strat, n, W,
           LAYOUT_NAME, sizeof(record_t));

    int64_t cs;
    if (strcmp(strat, "grow") == 0)
        cs = run_grow(n, W);
    else if (strcmp(strat, "heap") == 0)
        cs = run_heap(n, W);
    else if (strcmp(strat, "static") == 0)
        cs = run_static(n, W);
    else if (strcmp(strat, "ring") == 0)
        cs = run_ring(n, W);
    else {
        fprintf(stderr, "io: unknown --strategy=%s\n", strat);
        return 2;
    }
    return critter_finish(cs);
}
