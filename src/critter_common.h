/*
 * critter_common.h - shared infrastructure for the Critter memory lab.
 *
 * Everything a unit needs to (a) produce deterministic temperature data and
 * (b) report its own memory behaviour in a machine-parsable way.
 *
 * Report protocol: every metric is printed to stdout as a line
 *     @@key=value
 * and phase markers as
 *     @@phase=<name> vmrss_kb=.. vmhwm_kb=.. heap_cur=.. heap_peak=.. t_s=..
 * The Python harness (memlab/) parses these lines.
 *
 * Compile-time knobs (all optional):
 *   -DCRITTER_SAMPLE_TYPE=0|1|2   0=double, 1=float, 2=fixed16 (centi-degC)
 *   -DCRITTER_STACK_PROBE         paint/scan the stack to find the high-water
 *                                 mark.  This PERTURBS RSS (it touches ~1 MB of
 *                                 stack), so probe builds are only ever used
 *                                 for the stack metric, never for RSS.
 */
#ifndef CRITTER_COMMON_H
#define CRITTER_COMMON_H

#include <math.h>
#include <stddef.h>
#include <stdint.h>

/* ------------------------------------------------------------------------ */
/* Sample representation                                                     */
/* ------------------------------------------------------------------------ */
#define CRITTER_T_DOUBLE  0
#define CRITTER_T_FLOAT   1
#define CRITTER_T_FIXED16 2

#ifndef CRITTER_SAMPLE_TYPE
#define CRITTER_SAMPLE_TYPE CRITTER_T_DOUBLE
#endif

#if CRITTER_SAMPLE_TYPE == CRITTER_T_DOUBLE
typedef double sample_t;
#define CRITTER_SAMPLE_NAME "double"
static inline double   s_to_c(sample_t s) { return s; }
static inline sample_t c_to_s(double c)   { return c; }
#elif CRITTER_SAMPLE_TYPE == CRITTER_T_FLOAT
typedef float sample_t;
#define CRITTER_SAMPLE_NAME "float"
static inline double   s_to_c(sample_t s) { return (double)s; }
static inline sample_t c_to_s(double c)   { return (float)c; }
#elif CRITTER_SAMPLE_TYPE == CRITTER_T_FIXED16
typedef int16_t sample_t; /* centi-degrees Celsius: 2 bytes, 0.01 C resolution */
#define CRITTER_SAMPLE_NAME "fixed16"
static inline double s_to_c(sample_t s) { return (double)s * 0.01; }
static inline sample_t c_to_s(double c)
{
    long v = lrint(c * 100.0);
    if (v > INT16_MAX) v = INT16_MAX;
    if (v < INT16_MIN) v = INT16_MIN;
    return (sample_t)v;
}
#else
#error "unknown CRITTER_SAMPLE_TYPE"
#endif

/* ------------------------------------------------------------------------ */
/* Simulated machine-room temperature sensor (deterministic)                */
/*   ~22 C setpoint, HVAC compressor cycle, slow drift, sensor noise, and    */
/*   rare spike outliers (ADC glitches) that the memory unit must remove.    */
/* ------------------------------------------------------------------------ */
typedef struct {
    uint64_t state;
    uint64_t index;
} sensor_t;

void   sensor_init(sensor_t *s, uint64_t seed);
double sensor_read_c(sensor_t *s);

/* ------------------------------------------------------------------------ */
/* Command line: --key=value                                                 */
/* ------------------------------------------------------------------------ */
const char *arg_str(int argc, char **argv, const char *key, const char *def);
long        arg_long(int argc, char **argv, const char *key, long def);

/* ------------------------------------------------------------------------ */
/* Tracked heap: identical to malloc/free but counts requested bytes.        */
/* Uses malloc_usable_size() so no header is added (no measurement bias).    */
/* ------------------------------------------------------------------------ */
void *cm_malloc(size_t n);
void *cm_calloc(size_t count, size_t n);
void *cm_realloc(void *p, size_t n);
void  cm_free(void *p);
void *cm_xmalloc(size_t n, const char *what); /* exits with code 3 on OOM */
void  critter_oom(const char *what, size_t bytes);

/* ------------------------------------------------------------------------ */
/* Overlay arena: one region, carved by a bump pointer, reset between phases */
/* ------------------------------------------------------------------------ */
typedef struct {
    uint8_t *base;
    size_t   cap;
    size_t   used;
    size_t   peak;
} arena_t;

int    arena_init(arena_t *a, size_t cap);
void  *arena_alloc(arena_t *a, size_t n);
size_t arena_mark(const arena_t *a);
void   arena_release(arena_t *a, size_t mark);
void   arena_destroy(arena_t *a);

/* ------------------------------------------------------------------------ */
/* Reporting                                                                 */
/* ------------------------------------------------------------------------ */
void critter_begin(const char *unit);     /* call first thing in main()   */
void critter_phase(const char *name);     /* RSS/heap snapshot at a phase */
int  critter_finish(int64_t checksum);    /* call last; returns exit code */

#endif /* CRITTER_COMMON_H */
