/*
 * unit_mem.c - Critter memory-focused unit.
 *
 * Removes outliers (robust median/MAD rule) and summarizes the cleaned data
 * into fixed windows for off-line analysis.  Four implementations of the
 * same job, ordered from the junior-dev prototype to an embedded design:
 *
 *   --strategy=copy_sort  copy + qsort for the median, a separate double
 *                         deviation array + qsort for the MAD, a separate
 *                         cleaned array.  ~4 buffers of N.      [default]
 *   --strategy=inplace    one scratch copy reused for median and MAD via
 *                         quickselect; cleaned data compacted in place. ~2N
 *   --strategy=histogram  fixed 20001-bin histogram (0.01 C over -50..150 C)
 *                         in .bss gives median/MAD with no copy.   ~1N + 80 KB
 *   --strategy=streaming  per-window median/MAD on a W-sample buffer; the
 *                         full data set is never stored.            ~O(W)
 *
 * copy_sort and inplace compute identical results; histogram quantizes
 * the median to 0.01 C; streaming uses a local (per-window) robust rule.
 *
 *   --n=N  --window=W  (defaults 1000000, 1000)
 */
#include "critter_algo.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define H_MIN_C (-50.0)
#define H_RES_C (0.01)
#define H_BINS  20001
static uint32_t g_hist[H_BINS]; /* 80 KB in .bss: costs RSS only if touched */

static sample_t *acquire(size_t n)
{
    sample_t *x = (sample_t *)cm_xmalloc(n * sizeof *x, "raw");
    sensor_t  s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) x[i] = c_to_s(sensor_read_c(&s));
    critter_phase("acquire");
    return x;
}

static size_t summarize_all(const sample_t *x, size_t k, size_t W, summary_t *out)
{
    size_t nw = 0;
    for (size_t i = 0; i < k; i += W) {
        size_t len = (k - i < W) ? k - i : W;
        summarize_samples(x + i, len, &out[nw++]);
    }
    return nw;
}

static int64_t finish_summaries(const sample_t *clean, size_t k, size_t W)
{
    size_t     nwmax = k / W + 1;
    summary_t *sum   = (summary_t *)cm_xmalloc(nwmax * sizeof *sum, "summaries");
    size_t     nw    = summarize_all(clean, k, W, sum);
    critter_phase("summarize");
    int64_t cs = summary_checksum(sum, nw) + (int64_t)k;
    cm_free(sum);
    return cs;
}

/* ---- junior-dev prototype -------------------------------------------- */
static int64_t run_copy_sort(size_t n, size_t W, size_t *removed)
{
    sample_t *raw    = acquire(n);
    sample_t *sorted = (sample_t *)cm_xmalloc(n * sizeof *sorted, "sorted-copy");
    memcpy(sorted, raw, n * sizeof *raw);
    qsort(sorted, n, sizeof *sorted, cmp_sample);
    double med = median_sorted_sample(sorted, n);

    double *dev = (double *)cm_xmalloc(n * sizeof *dev, "deviations");
    for (size_t i = 0; i < n; i++) dev[i] = fabs(s_to_c(raw[i]) - med);
    qsort(dev, n, sizeof *dev, cmp_double);
    double mad = median_sorted_double(dev, n);
    double lim = outlier_limit(mad);

    sample_t *clean = (sample_t *)cm_xmalloc(n * sizeof *clean, "cleaned");
    size_t    k     = 0;
    for (size_t i = 0; i < n; i++)
        if (fabs(s_to_c(raw[i]) - med) <= lim) clean[k++] = raw[i];
    critter_phase("filter");

    int64_t cs = finish_summaries(clean, k, W);
    *removed   = n - k;
    cm_free(raw);
    cm_free(sorted);
    cm_free(dev);
    cm_free(clean);
    return cs;
}

/* ---- one scratch buffer, quickselect, in-place compaction ------------ */
static int64_t run_inplace(size_t n, size_t W, size_t *removed)
{
    sample_t *raw     = acquire(n);
    sample_t *scratch = (sample_t *)cm_xmalloc(n * sizeof *scratch, "scratch");
    memcpy(scratch, raw, n * sizeof *raw);
    double med = median_select(scratch, n);
    for (size_t i = 0; i < n; i++) scratch[i] = c_to_s(fabs(s_to_c(raw[i]) - med));
    double mad = median_select(scratch, n);
    cm_free(scratch); /* released before the next allocation */
    double lim = outlier_limit(mad);

    size_t k = 0;
    for (size_t i = 0; i < n; i++)
        if (fabs(s_to_c(raw[i]) - med) <= lim) raw[k++] = raw[i];
    critter_phase("filter");

    int64_t cs = finish_summaries(raw, k, W);
    *removed   = n - k;
    cm_free(raw);
    return cs;
}

/* ---- fixed-size histogram: memory independent of N ------------------- */
static size_t hist_bin(double v)
{
    long b = lrint((v - H_MIN_C) / H_RES_C);
    if (b < 0) b = 0;
    if (b >= H_BINS) b = H_BINS - 1;
    return (size_t)b;
}

static size_t hist_rank(size_t rank)
{
    size_t cum = 0;
    for (size_t b = 0; b < H_BINS; b++) {
        cum += g_hist[b];
        if (cum > rank) return b;
    }
    return H_BINS - 1;
}

static int64_t run_histogram(size_t n, size_t W, size_t *removed)
{
    sample_t *raw = acquire(n);

    memset(g_hist, 0, sizeof g_hist);
    for (size_t i = 0; i < n; i++) g_hist[hist_bin(s_to_c(raw[i]))]++;
    double med = H_MIN_C + (double)hist_rank(n / 2) * H_RES_C;

    memset(g_hist, 0, sizeof g_hist);
    for (size_t i = 0; i < n; i++) {
        long b = lrint(fabs(s_to_c(raw[i]) - med) / H_RES_C);
        if (b >= H_BINS) b = H_BINS - 1;
        g_hist[b]++;
    }
    double mad = (double)hist_rank(n / 2) * H_RES_C;
    double lim = outlier_limit(mad);

    size_t k = 0;
    for (size_t i = 0; i < n; i++)
        if (fabs(s_to_c(raw[i]) - med) <= lim) raw[k++] = raw[i];
    critter_phase("filter");

    int64_t cs = finish_summaries(raw, k, W);
    *removed   = n - k;
    cm_free(raw);
    return cs;
}

/* ---- streaming: only one window is ever resident ---------------------- */
static int64_t run_streaming(size_t n, size_t W, size_t *removed)
{
    sample_t  *win  = (sample_t *)cm_xmalloc(W * sizeof *win, "window");
    sample_t  *scr  = (sample_t *)cm_xmalloc(W * sizeof *scr, "window-scratch");
    summary_t *sum  = (summary_t *)cm_xmalloc((n / W + 1) * sizeof *sum, "summaries");
    size_t     nw   = 0, kept = 0;
    sensor_t   s;
    sensor_init(&s, 42);

    for (size_t start = 0; start < n; start += W) {
        size_t len = (n - start < W) ? n - start : W;
        for (size_t i = 0; i < len; i++) win[i] = c_to_s(sensor_read_c(&s));
        memcpy(scr, win, len * sizeof *win);
        double med = median_select(scr, len);
        for (size_t i = 0; i < len; i++) scr[i] = c_to_s(fabs(s_to_c(win[i]) - med));
        double mad = median_select(scr, len);
        double lim = outlier_limit(mad);
        size_t k   = 0;
        for (size_t i = 0; i < len; i++)
            if (fabs(s_to_c(win[i]) - med) <= lim) win[k++] = win[i];
        summarize_samples(win, k, &sum[nw++]);
        kept += k;
    }
    critter_phase("acquire+filter+summarize");
    int64_t cs = summary_checksum(sum, nw) + (int64_t)kept;
    *removed   = n - kept;
    cm_free(win);
    cm_free(scr);
    cm_free(sum);
    return cs;
}

int main(int argc, char **argv)
{
    critter_begin("mem");
    size_t      n     = (size_t)arg_long(argc, argv, "n", 1000000);
    size_t      W     = (size_t)arg_long(argc, argv, "window", 1000);
    const char *strat = arg_str(argc, argv, "strategy", "copy_sort");
    if (W == 0) W = 1;
    if (n == 0) n = 1;
    printf("@@strategy=%s\n@@n=%zu\n@@window=%zu\n", strat, n, W);

    size_t  removed = 0;
    int64_t cs;
    if (strcmp(strat, "copy_sort") == 0)
        cs = run_copy_sort(n, W, &removed);
    else if (strcmp(strat, "inplace") == 0)
        cs = run_inplace(n, W, &removed);
    else if (strcmp(strat, "histogram") == 0)
        cs = run_histogram(n, W, &removed);
    else if (strcmp(strat, "streaming") == 0)
        cs = run_streaming(n, W, &removed);
    else {
        fprintf(stderr, "mem: unknown --strategy=%s\n", strat);
        return 2;
    }
    printf("@@outliers_removed=%zu\n", removed);
    return critter_finish(cs);
}
