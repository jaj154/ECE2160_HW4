/*
 * critter_algo.h - algorithms shared by the units and the pipeline.
 */
#ifndef CRITTER_ALGO_H
#define CRITTER_ALGO_H

#include "critter_common.h"

#define CRITTER_MAXP     32     /* max autoregressive order              */
#define CRITTER_CENTER_C 22.0   /* data are centred on the setpoint      */
#define CRITTER_MODZ     3.5    /* modified z-score outlier threshold    */
#define CRITTER_MAD_MIN  0.05   /* MAD floor (C) so flat data never divides by 0 */

/* |x - median| above this is an outlier (Iglewicz & Hoaglin modified z). */
static inline double outlier_limit(double mad)
{
    if (mad < CRITTER_MAD_MIN) mad = CRITTER_MAD_MIN;
    return CRITTER_MODZ * mad / 0.6745;
}

/* comparison helpers for qsort */
int cmp_sample(const void *a, const void *b);
int cmp_double(const void *a, const void *b);

/* In-place selection (no extra memory). Reorders a[]. Returns degrees C. */
sample_t select_kth(sample_t *a, size_t n, size_t k);
double   median_select(sample_t *a, size_t n);
double   median_sorted_sample(const sample_t *a, size_t n);
double   median_sorted_double(const double *a, size_t n);

/* window summaries used for off-line analysis (32 bytes each) */
typedef struct {
    double   mean, min, max;
    uint64_t count;
} summary_t;

void    summarize_samples(const sample_t *x, size_t n, summary_t *out);
int64_t summary_checksum(const summary_t *s, size_t ns);

/* dense linear algebra (junior-dev style, the undergrad prototypes) */
void matmul(const double *A, const double *B, double *C, size_t n, size_t m, size_t p);
void transpose(const double *A, double *At, size_t rows, size_t cols);
int  gauss_solve(double *aug, int p); /* aug is p x (p+1); solution in last column */

#endif /* CRITTER_ALGO_H */
