/*
 * pipeline.c - the whole Critter (acquire -> clean -> predict) in one
 * binary, used to study how buffers from different phases coexist.
 *
 *   --mode=concurrent  every buffer allocated up front, freed at exit
 *                      (peak = SUM of all phases)          [junior default]
 *   --mode=phased      allocate per phase, free as soon as dead
 *                      (peak = MAX phase, but depends on the allocator)
 *   --mode=overlay     ONE arena sized for the largest phase; later phases
 *                      reuse the memory of earlier ones (classic overlay
 *                      applied to data; deterministic, no allocator churn)
 *   --fit=materialized|streaming   how the predict phase fits AR(p)
 *
 * Process-level overlay (one process per phase, data handed off by file):
 *   --stage=acquire --handoff=PREFIX   writes PREFIX.raw
 *   --stage=clean   --handoff=PREFIX   reads .raw, writes PREFIX.clean
 *   --stage=predict --handoff=PREFIX   reads .clean, prints final checksum
 * The final checksum equals --stage=all for every mode.
 *
 *   --n=N --p=8 (defaults 1000000, 8)
 */
#include "critter_algo.h"

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define FORECAST_STEPS 1000

/* ---- phase 1 ---------------------------------------------------------- */
static void acquire(sample_t *raw, size_t n)
{
    sensor_t s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) raw[i] = c_to_s(sensor_read_c(&s));
}

/* ---- phase 2: dst may alias raw (in-place compaction is safe) --------- */
static size_t clean_into(const sample_t *raw, size_t n, sample_t *scratch, sample_t *dst)
{
    memcpy(scratch, raw, n * sizeof *raw);
    double med = median_select(scratch, n);
    for (size_t i = 0; i < n; i++) scratch[i] = c_to_s(fabs(s_to_c(raw[i]) - med));
    double mad = median_select(scratch, n);
    double lim = outlier_limit(mad);
    size_t k   = 0;
    for (size_t i = 0; i < n; i++) {
        sample_t v = raw[i];
        if (fabs(s_to_c(v) - med) <= lim) dst[k++] = v;
    }
    return k;
}

/* ---- phase 3 ---------------------------------------------------------- */
static void fit_materialized(const sample_t *x, size_t k, int p, double *X, double *Xt, double *y, double *xtx,
                             double *xty)
{
    size_t m = k - (size_t)p;
    for (size_t r = 0; r < m; r++) {
        size_t t = r + (size_t)p;
        for (int j = 0; j < p; j++) X[r * (size_t)p + (size_t)j] = s_to_c(x[t - 1 - (size_t)j]) - CRITTER_CENTER_C;
        y[r] = s_to_c(x[t]) - CRITTER_CENTER_C;
    }
    transpose(X, Xt, m, (size_t)p);
    matmul(Xt, X, xtx, (size_t)p, m, (size_t)p);
    matmul(Xt, y, xty, (size_t)p, m, 1);
}

static void fit_streaming(const sample_t *x, size_t k, int p, double *xtx, double *xty)
{
    memset(xtx, 0, sizeof(double) * (size_t)(p * p));
    memset(xty, 0, sizeof(double) * (size_t)p);
    for (size_t t = (size_t)p; t < k; t++) {
        double v = s_to_c(x[t]) - CRITTER_CENTER_C;
        for (int j = 0; j < p; j++) {
            double fj = s_to_c(x[t - 1 - (size_t)j]) - CRITTER_CENTER_C;
            for (int c = 0; c < p; c++) xtx[j * p + c] += fj * (s_to_c(x[t - 1 - (size_t)c]) - CRITTER_CENTER_C);
            xty[j] += fj * v;
        }
    }
}

static int64_t predict_checksum(const sample_t *x, size_t k, int p, const double *xtx, const double *xty)
{
    double aug[CRITTER_MAXP * (CRITTER_MAXP + 1)], coef[CRITTER_MAXP], hist[CRITTER_MAXP];
    for (int r = 0; r < p; r++) {
        for (int c = 0; c < p; c++) aug[r * (p + 1) + c] = xtx[r * p + c];
        aug[r * (p + 1) + p] = xty[r];
    }
    if (gauss_solve(aug, p) != 0) printf("@@warning=singular_system\n");
    for (int j = 0; j < p; j++) coef[j] = aug[j * (p + 1) + p];
    for (int j = 0; j < p; j++) hist[j] = s_to_c(x[k - (size_t)p + (size_t)j]) - CRITTER_CENTER_C;

    double peak = -1e300;
    for (int step = 0; step < FORECAST_STEPS; step++) {
        double yhat = 0.0;
        for (int j = 0; j < p; j++) yhat += coef[j] * hist[p - 1 - j];
        memmove(hist, hist + 1, (size_t)(p - 1) * sizeof *hist);
        hist[p - 1] = yhat;
        if (yhat + CRITTER_CENTER_C > peak) peak = yhat + CRITTER_CENTER_C;
    }
    int64_t cs = llround(peak * 1000.0) + (int64_t)k;
    for (int j = 0; j < p; j++) cs += llround(coef[j] * 1e6);
    printf("@@kept=%zu\n@@forecast_peak_c=%.4f\n", k, peak);
    return cs;
}

static size_t design_bytes(size_t k, int p, int materialized)
{
    if (!materialized || k <= (size_t)p) return 0;
    size_t m = k - (size_t)p;
    return (2u * m * (size_t)p + m) * sizeof(double);
}

/* ---- memory plans ------------------------------------------------------ */
static int64_t run_concurrent(size_t n, int p, int mat)
{
    size_t    m       = n - (size_t)p;
    sample_t *raw     = (sample_t *)cm_xmalloc(n * sizeof *raw, "raw");
    sample_t *scratch = (sample_t *)cm_xmalloc(n * sizeof *scratch, "scratch");
    sample_t *clean   = (sample_t *)cm_xmalloc(n * sizeof *clean, "clean");
    double   *X = NULL, *Xt = NULL, *y = NULL;
    if (mat) {
        X  = (double *)cm_xmalloc(m * (size_t)p * sizeof *X, "X");
        Xt = (double *)cm_xmalloc(m * (size_t)p * sizeof *Xt, "Xt");
        y  = (double *)cm_xmalloc(m * sizeof *y, "y");
    }
    double xtx[CRITTER_MAXP * CRITTER_MAXP], xty[CRITTER_MAXP];
    acquire(raw, n);
    critter_phase("acquire");
    size_t k = clean_into(raw, n, scratch, clean);
    critter_phase("clean");
    if (mat)
        fit_materialized(clean, k, p, X, Xt, y, xtx, xty);
    else
        fit_streaming(clean, k, p, xtx, xty);
    critter_phase("predict");
    int64_t cs = predict_checksum(clean, k, p, xtx, xty);
    cm_free(raw);
    cm_free(scratch);
    cm_free(clean);
    cm_free(X);
    cm_free(Xt);
    cm_free(y);
    return cs;
}

static int64_t run_phased(size_t n, int p, int mat)
{
    sample_t *raw = (sample_t *)cm_xmalloc(n * sizeof *raw, "raw");
    acquire(raw, n);
    critter_phase("acquire");

    sample_t *scratch = (sample_t *)cm_xmalloc(n * sizeof *scratch, "scratch");
    sample_t *clean   = (sample_t *)cm_xmalloc(n * sizeof *clean, "clean");
    size_t    k       = clean_into(raw, n, scratch, clean);
    cm_free(scratch);
    cm_free(raw);
    critter_phase("clean");

    double xtx[CRITTER_MAXP * CRITTER_MAXP], xty[CRITTER_MAXP];
    if (mat) {
        size_t  m  = k - (size_t)p;
        double *X  = (double *)cm_xmalloc(m * (size_t)p * sizeof *X, "X");
        double *Xt = (double *)cm_xmalloc(m * (size_t)p * sizeof *Xt, "Xt");
        double *y  = (double *)cm_xmalloc(m * sizeof *y, "y");
        fit_materialized(clean, k, p, X, Xt, y, xtx, xty);
        cm_free(X);
        cm_free(Xt);
        cm_free(y);
    } else {
        fit_streaming(clean, k, p, xtx, xty);
    }
    critter_phase("predict");
    int64_t cs = predict_checksum(clean, k, p, xtx, xty);
    cm_free(clean);
    return cs;
}

static int64_t run_overlay(size_t n, int p, int mat)
{
    /* region A holds raw, later the cleaned data (compacted in place);
     * region B holds the clean-phase scratch, later the design matrix. */
    size_t  a_bytes = n * sizeof(sample_t);
    size_t  b_need  = design_bytes(n, p, mat);
    size_t  b_bytes = a_bytes > b_need ? a_bytes : b_need;
    arena_t ar;
    if (arena_init(&ar, a_bytes + b_bytes + 256u) != 0) critter_oom("overlay-arena", a_bytes + b_bytes);
    printf("@@overlay_arena_bytes=%zu\n", ar.cap);

    sample_t *raw = (sample_t *)arena_alloc(&ar, a_bytes);
    acquire(raw, n);
    critter_phase("acquire");

    size_t    mark    = arena_mark(&ar);
    sample_t *scratch = (sample_t *)arena_alloc(&ar, a_bytes);
    size_t    k       = clean_into(raw, n, scratch, raw); /* clean overlays raw */
    arena_release(&ar, mark);                              /* scratch is dead   */
    critter_phase("clean");

    double xtx[CRITTER_MAXP * CRITTER_MAXP], xty[CRITTER_MAXP];
    if (mat) {
        size_t  m  = k - (size_t)p;
        double *X  = (double *)arena_alloc(&ar, m * (size_t)p * sizeof(double)); /* overlays scratch */
        double *Xt = (double *)arena_alloc(&ar, m * (size_t)p * sizeof(double));
        double *y  = (double *)arena_alloc(&ar, m * sizeof(double));
        if (!X || !Xt || !y) critter_oom("overlay-design", design_bytes(k, p, 1));
        fit_materialized(raw, k, p, X, Xt, y, xtx, xty);
    } else {
        fit_streaming(raw, k, p, xtx, xty);
    }
    critter_phase("predict");
    int64_t cs = predict_checksum(raw, k, p, xtx, xty);
    printf("@@overlay_arena_peak_bytes=%zu\n", ar.peak);
    arena_destroy(&ar);
    return cs;
}

/* ---- process-level staging ---------------------------------------------- */
static void write_blob(const char *path, const sample_t *x, size_t k)
{
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror(path); exit(4); }
    uint64_t hdr = k;
    if (write(fd, &hdr, sizeof hdr) != (ssize_t)sizeof hdr) { perror("write"); exit(4); }
    const char *p   = (const char *)x;
    size_t      rem = k * sizeof *x;
    while (rem) {
        ssize_t w = write(fd, p, rem);
        if (w <= 0) { perror("write"); exit(4); }
        p += w;
        rem -= (size_t)w;
    }
    close(fd);
}

static sample_t *read_blob(const char *path, size_t *k_out)
{
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror(path); exit(4); }
    uint64_t hdr = 0;
    if (read(fd, &hdr, sizeof hdr) != (ssize_t)sizeof hdr) { perror("read"); exit(4); }
    sample_t *x   = (sample_t *)cm_xmalloc((size_t)hdr * sizeof *x, "handoff");
    char     *p   = (char *)x;
    size_t    rem = (size_t)hdr * sizeof *x;
    while (rem) {
        ssize_t r = read(fd, p, rem);
        if (r <= 0) { perror("read"); exit(4); }
        p += r;
        rem -= (size_t)r;
    }
    close(fd);
    *k_out = (size_t)hdr;
    return x;
}

static int64_t run_stage(const char *stage, const char *prefix, size_t n, int p, int mat)
{
    char path_raw[512], path_clean[512];
    snprintf(path_raw, sizeof path_raw, "%s.raw", prefix);
    snprintf(path_clean, sizeof path_clean, "%s.clean", prefix);

    if (strcmp(stage, "acquire") == 0) {
        sample_t *raw = (sample_t *)cm_xmalloc(n * sizeof *raw, "raw");
        acquire(raw, n);
        critter_phase("acquire");
        write_blob(path_raw, raw, n);
        cm_free(raw);
        return (int64_t)n;
    }
    if (strcmp(stage, "clean") == 0) {
        size_t    nn;
        sample_t *raw     = read_blob(path_raw, &nn);
        sample_t *scratch = (sample_t *)cm_xmalloc(nn * sizeof *scratch, "scratch");
        size_t    k       = clean_into(raw, nn, scratch, raw);
        cm_free(scratch);
        critter_phase("clean");
        write_blob(path_clean, raw, k);
        cm_free(raw);
        return (int64_t)k;
    }
    if (strcmp(stage, "predict") == 0) {
        size_t    k;
        sample_t *x = read_blob(path_clean, &k);
        double    xtx[CRITTER_MAXP * CRITTER_MAXP], xty[CRITTER_MAXP];
        if (mat) {
            size_t  m  = k - (size_t)p;
            double *X  = (double *)cm_xmalloc(m * (size_t)p * sizeof *X, "X");
            double *Xt = (double *)cm_xmalloc(m * (size_t)p * sizeof *Xt, "Xt");
            double *y  = (double *)cm_xmalloc(m * sizeof *y, "y");
            fit_materialized(x, k, p, X, Xt, y, xtx, xty);
            cm_free(X);
            cm_free(Xt);
            cm_free(y);
        } else {
            fit_streaming(x, k, p, xtx, xty);
        }
        critter_phase("predict");
        int64_t cs = predict_checksum(x, k, p, xtx, xty);
        cm_free(x);
        return cs;
    }
    fprintf(stderr, "pipeline: unknown --stage=%s\n", stage);
    exit(2);
}

int main(int argc, char **argv)
{
    critter_begin("pipeline");
    size_t      n     = (size_t)arg_long(argc, argv, "n", 1000000);
    int         p     = (int)arg_long(argc, argv, "p", 8);
    const char *mode  = arg_str(argc, argv, "mode", "concurrent");
    const char *fit   = arg_str(argc, argv, "fit", "materialized");
    const char *stage = arg_str(argc, argv, "stage", "all");
    const char *pre   = arg_str(argc, argv, "handoff", "/tmp/critter_handoff");
    if (p < 1) p = 1;
    if (p > CRITTER_MAXP) p = CRITTER_MAXP;
    if (n < (size_t)(4 * p)) n = (size_t)(4 * p);
    int mat = strcmp(fit, "streaming") != 0;
    printf("@@mode=%s\n@@fit=%s\n@@stage=%s\n@@n=%zu\n@@p=%d\n", mode, mat ? "materialized" : "streaming", stage, n,
           p);

    int64_t cs;
    if (strcmp(stage, "all") != 0)
        cs = run_stage(stage, pre, n, p, mat);
    else if (strcmp(mode, "concurrent") == 0)
        cs = run_concurrent(n, p, mat);
    else if (strcmp(mode, "phased") == 0)
        cs = run_phased(n, p, mat);
    else if (strcmp(mode, "overlay") == 0)
        cs = run_overlay(n, p, mat);
    else {
        fprintf(stderr, "pipeline: unknown --mode=%s\n", mode);
        return 2;
    }
    return critter_finish(cs);
}
