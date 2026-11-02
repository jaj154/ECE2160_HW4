/*
 * critter_algo.c - selection, summaries and dense linear algebra.
 */
#include "critter_algo.h"

#include <math.h>
#include <string.h>

int cmp_sample(const void *a, const void *b)
{
    sample_t x = *(const sample_t *)a, y = *(const sample_t *)b;
    return (x > y) - (x < y);
}

int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

/* Iterative Hoare-style quickselect: O(n) average, O(1) extra memory,
 * no recursion (so its stack use does not depend on n). */
sample_t select_kth(sample_t *a, size_t n, size_t k)
{
    ptrdiff_t lo = 0, hi = (ptrdiff_t)n - 1, kk = (ptrdiff_t)k;
    while (lo < hi) {
        sample_t  pivot = a[lo + (hi - lo) / 2];
        ptrdiff_t i = lo, j = hi;
        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;
            if (i <= j) {
                sample_t t = a[i];
                a[i] = a[j];
                a[j] = t;
                i++;
                j--;
            }
        }
        if (kk <= j)
            hi = j;
        else if (kk >= i)
            lo = i;
        else
            return a[kk];
    }
    return a[kk];
}

double median_select(sample_t *a, size_t n)
{
    if (n == 0) return 0.0;
    sample_t upper = select_kth(a, n, n / 2);
    if (n & 1u) return s_to_c(upper);
    /* even n: lower middle is the max of the left partition */
    sample_t lower = a[0];
    for (size_t i = 1; i < n / 2; i++)
        if (a[i] > lower) lower = a[i];
    return 0.5 * (s_to_c(lower) + s_to_c(upper));
}

double median_sorted_sample(const sample_t *a, size_t n)
{
    if (n == 0) return 0.0;
    if (n & 1u) return s_to_c(a[n / 2]);
    return 0.5 * (s_to_c(a[n / 2 - 1]) + s_to_c(a[n / 2]));
}

double median_sorted_double(const double *a, size_t n)
{
    if (n == 0) return 0.0;
    if (n & 1u) return a[n / 2];
    return 0.5 * (a[n / 2 - 1] + a[n / 2]);
}

void summarize_samples(const sample_t *x, size_t n, summary_t *out)
{
    double sum = 0.0, mn = 1e300, mx = -1e300;
    for (size_t i = 0; i < n; i++) {
        double c = s_to_c(x[i]);
        sum += c;
        if (c < mn) mn = c;
        if (c > mx) mx = c;
    }
    out->mean  = n ? sum / (double)n : 0.0;
    out->min   = n ? mn : 0.0;
    out->max   = n ? mx : 0.0;
    out->count = n;
}

int64_t summary_checksum(const summary_t *s, size_t ns)
{
    int64_t cs = 0;
    for (size_t i = 0; i < ns; i++)
        cs += llround(s[i].mean * 1000.0) + llround(s[i].min * 1000.0) + llround(s[i].max * 1000.0) +
              (int64_t)s[i].count;
    return cs;
}

/* C[n x p] = A[n x m] * B[m x p], inner-product order (k ascending). */
void matmul(const double *A, const double *B, double *C, size_t n, size_t m, size_t p)
{
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < p; j++) {
            double acc = 0.0;
            for (size_t k = 0; k < m; k++) acc += A[i * m + k] * B[k * p + j];
            C[i * p + j] = acc;
        }
}

void transpose(const double *A, double *At, size_t rows, size_t cols)
{
    for (size_t r = 0; r < rows; r++)
        for (size_t c = 0; c < cols; c++) At[c * rows + r] = A[r * cols + c];
}

int gauss_solve(double *aug, int p)
{
    const int w = p + 1;
    for (int col = 0; col < p; col++) {
        int    piv  = col;
        double best = fabs(aug[col * w + col]);
        for (int r = col + 1; r < p; r++)
            if (fabs(aug[r * w + col]) > best) {
                best = fabs(aug[r * w + col]);
                piv  = r;
            }
        if (best < 1e-12) return -1;
        if (piv != col)
            for (int c = 0; c < w; c++) {
                double t         = aug[col * w + c];
                aug[col * w + c] = aug[piv * w + c];
                aug[piv * w + c] = t;
            }
        for (int r = 0; r < p; r++) {
            if (r == col) continue;
            double f = aug[r * w + col] / aug[col * w + col];
            for (int c = col; c < w; c++) aug[r * w + c] -= f * aug[col * w + c];
        }
    }
    for (int r = 0; r < p; r++) aug[r * w + p] /= aug[r * w + r];
    return 0;
}
