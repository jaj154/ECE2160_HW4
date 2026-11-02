/*
 * unit_compute.c - Critter computationally intensive unit.
 *
 * Predicts HVAC behaviour with an autoregressive AR(p) model:
 *   1. fit    least squares on lagged temperatures
 *   2. forecast  H steps ahead (written recursively, as a junior dev would:
 *              it is tail recursive, so the compiler MAY turn it into a loop)
 *   3. scenarios  binary tree of "HVAC keeps up / HVAC fails" futures,
 *              depth D (genuine recursion, frames hold local arrays)
 *
 *   --mode=materialized  build X (N x p), an explicit transpose Xt, and y,
 *                        then XtX = Xt*X by matrix multiplication. [default]
 *   --mode=streaming     accumulate XtX and Xty sample by sample; only a
 *                        p-sample history is stored.
 *   --scratch=heap|stack|static   where the solver workspace lives
 *                        (p x (p+1) system + 4096-double trajectory buffer)
 *   --n=N --p=8 --horizon=4000 --depth=10
 *
 * Both modes sum in the same order, so they give identical coefficients.
 */
#include "critter_algo.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CRITTER_WORK 4096 /* trajectory buffer, doubles (32 KB) */

static double g_static_aug[CRITTER_MAXP * (CRITTER_MAXP + 1)];
static double g_static_work[CRITTER_WORK];

/* ---- step 2: recursive forecast (tail call) ---------------------------- */
__attribute__((noinline)) static double forecast_rec(const double *coef, int p, double *hist, int pos,
                                                     int remaining, double peak, double *traj, int step)
{
    if (remaining <= 0) return peak;
    double yhat = 0.0;
    for (int j = 0; j < p; j++) yhat += coef[j] * hist[(pos - 1 - j + p) % p];
    hist[pos]  = yhat;
    traj[step] = yhat + CRITTER_CENTER_C;
    if (traj[step] > peak) peak = traj[step];
    return forecast_rec(coef, p, hist, (pos + 1) % p, remaining - 1, peak, traj, step + 1);
}

/* ---- step 3: scenario tree (true recursion, local arrays per frame) ---- */
static double scenario(const double *coef, int p, const double *hist_in, int depth)
{
    double hist[CRITTER_MAXP];
    memcpy(hist, hist_in, (size_t)p * sizeof *hist);
    double yhat = 0.0;
    for (int j = 0; j < p; j++) yhat += coef[j] * hist[p - 1 - j];
    if (depth == 0) return yhat + CRITTER_CENTER_C;

    double best = -1e300;
    for (int branch = 0; branch < 2; branch++) {
        double next[CRITTER_MAXP];
        memcpy(next, hist + 1, (size_t)(p - 1) * sizeof *next);
        next[p - 1] = yhat + (branch ? 0.05 : -0.02); /* HVAC fails : HVAC keeps up */
        double v    = scenario(coef, p, next, depth - 1);
        if (v > best) best = v;
    }
    return best;
}

/* ---- solve + forecast with caller-provided workspace ------------------- */
static int64_t solve_forecast(double *aug, double *work, const double *xtx, const double *xty, int p,
                              const double *hist_lin, int horizon, int depth)
{
    for (int r = 0; r < p; r++) {
        for (int c = 0; c < p; c++) aug[r * (p + 1) + c] = xtx[r * p + c];
        aug[r * (p + 1) + p] = xty[r];
    }
    if (gauss_solve(aug, p) != 0) {
        printf("@@warning=singular_system\n");
        return 0;
    }
    double coef[CRITTER_MAXP], hist[CRITTER_MAXP];
    for (int j = 0; j < p; j++) coef[j] = aug[j * (p + 1) + p];
    memcpy(hist, hist_lin, (size_t)p * sizeof *hist);

    double peak = forecast_rec(coef, p, hist, 0, horizon, -1e300, work, 0);
    double mean = 0.0;
    for (int i = 0; i < horizon; i++) mean += work[i];
    mean /= (double)(horizon > 0 ? horizon : 1);
    critter_phase("forecast");

    double worst = scenario(coef, p, hist_lin, depth);
    critter_phase("scenarios");

    int64_t cs = llround(peak * 1000.0) + llround(mean * 1000.0) + llround(worst * 1000.0);
    for (int j = 0; j < p; j++) cs += llround(coef[j] * 1e6);
    printf("@@forecast_peak_c=%.4f\n@@scenario_worst_c=%.4f\n", peak, worst);
    return cs;
}

__attribute__((noinline)) static int64_t scratch_on_stack(const double *xtx, const double *xty, int p,
                                                          const double *hist, int h, int d)
{
    double aug[CRITTER_MAXP * (CRITTER_MAXP + 1)]; /* 8.4 KB */
    double work[CRITTER_WORK];                      /* 32 KB  */
    return solve_forecast(aug, work, xtx, xty, p, hist, h, d);
}

static int64_t scratch_on_heap(const double *xtx, const double *xty, int p, const double *hist, int h, int d)
{
    double *aug  = (double *)cm_xmalloc(sizeof(double) * CRITTER_MAXP * (CRITTER_MAXP + 1), "aug");
    double *work = (double *)cm_xmalloc(sizeof(double) * CRITTER_WORK, "work");
    int64_t cs   = solve_forecast(aug, work, xtx, xty, p, hist, h, d);
    cm_free(aug);
    cm_free(work);
    return cs;
}

/* ---- step 1 variants ---------------------------------------------------- */
static void fit_materialized(size_t n, int p, double *xtx, double *xty, double *hist_lin)
{
    sample_t *x = (sample_t *)cm_xmalloc(n * sizeof *x, "input");
    sensor_t  s;
    sensor_init(&s, 42);
    for (size_t i = 0; i < n; i++) x[i] = c_to_s(sensor_read_c(&s));
    critter_phase("acquire");

    size_t  m  = n - (size_t)p;
    double *X  = (double *)cm_xmalloc(m * (size_t)p * sizeof *X, "design-matrix");
    double *Xt = (double *)cm_xmalloc(m * (size_t)p * sizeof *Xt, "design-transpose");
    double *y  = (double *)cm_xmalloc(m * sizeof *y, "targets");
    for (size_t r = 0; r < m; r++) {
        size_t t = r + (size_t)p;
        for (int j = 0; j < p; j++) X[r * (size_t)p + (size_t)j] = s_to_c(x[t - 1 - (size_t)j]) - CRITTER_CENTER_C;
        y[r] = s_to_c(x[t]) - CRITTER_CENTER_C;
    }
    transpose(X, Xt, m, (size_t)p);
    critter_phase("build-design");
    matmul(Xt, X, xtx, (size_t)p, m, (size_t)p);
    matmul(Xt, y, xty, (size_t)p, m, 1);
    critter_phase("fit");
    for (int j = 0; j < p; j++) hist_lin[j] = s_to_c(x[n - (size_t)p + (size_t)j]) - CRITTER_CENTER_C;
    cm_free(X);
    cm_free(Xt);
    cm_free(y);
    cm_free(x);
}

static void fit_streaming(size_t n, int p, double *xtx, double *xty, double *hist_lin)
{
    double   ring[CRITTER_MAXP], f[CRITTER_MAXP];
    int      pos = 0;
    sensor_t s;
    sensor_init(&s, 42);
    memset(xtx, 0, sizeof(double) * (size_t)p * (size_t)p);
    memset(xty, 0, sizeof(double) * (size_t)p);
    for (size_t t = 0; t < n; t++) {
        double v = s_to_c(c_to_s(sensor_read_c(&s))) - CRITTER_CENTER_C;
        if (t >= (size_t)p) {
            for (int j = 0; j < p; j++) f[j] = ring[(pos - 1 - j + p) % p];
            for (int j = 0; j < p; j++) {
                for (int k = 0; k < p; k++) xtx[j * p + k] += f[j] * f[k];
                xty[j] += f[j] * v;
            }
        }
        ring[pos] = v;
        pos       = (pos + 1) % p;
    }
    for (int i = 0; i < p; i++) hist_lin[i] = ring[(pos + i) % p];
    critter_phase("fit");
}

int main(int argc, char **argv)
{
    critter_begin("compute");
    size_t      n       = (size_t)arg_long(argc, argv, "n", 1000000);
    int         p       = (int)arg_long(argc, argv, "p", 8);
    int         horizon = (int)arg_long(argc, argv, "horizon", 4000);
    int         depth   = (int)arg_long(argc, argv, "depth", 10);
    const char *mode    = arg_str(argc, argv, "mode", "materialized");
    const char *scr     = arg_str(argc, argv, "scratch", "heap");
    if (p < 1) p = 1;
    if (p > CRITTER_MAXP) p = CRITTER_MAXP;
    if (horizon > CRITTER_WORK) horizon = CRITTER_WORK;
    if (horizon < 1) horizon = 1;
    if (n < (size_t)p + 2) n = (size_t)p + 2;
    printf("@@mode=%s\n@@scratch=%s\n@@n=%zu\n@@p=%d\n@@horizon=%d\n@@depth=%d\n", mode, scr, n, p, horizon,
           depth);

    double xtx[CRITTER_MAXP * CRITTER_MAXP], xty[CRITTER_MAXP], hist[CRITTER_MAXP];
    if (strcmp(mode, "materialized") == 0)
        fit_materialized(n, p, xtx, xty, hist);
    else if (strcmp(mode, "streaming") == 0)
        fit_streaming(n, p, xtx, xty, hist);
    else {
        fprintf(stderr, "compute: unknown --mode=%s\n", mode);
        return 2;
    }

    int64_t cs;
    if (strcmp(scr, "stack") == 0)
        cs = scratch_on_stack(xtx, xty, p, hist, horizon, depth);
    else if (strcmp(scr, "static") == 0)
        cs = solve_forecast(g_static_aug, g_static_work, xtx, xty, p, hist, horizon, depth);
    else if (strcmp(scr, "heap") == 0)
        cs = scratch_on_heap(xtx, xty, p, hist, horizon, depth);
    else {
        fprintf(stderr, "compute: unknown --scratch=%s\n", scr);
        return 2;
    }
    return critter_finish(cs);
}
