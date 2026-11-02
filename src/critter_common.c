/*
 * critter_common.c - instrumentation and shared services for the Critter lab.
 *
 * Design rule: measurement code must not distort what it measures.
 *   - /proc/self/status is read with open()/read() into a static buffer,
 *     so taking a snapshot never calls malloc.
 *   - Heap accounting uses malloc_usable_size() instead of a size header.
 *   - The stack probe only exists in -DCRITTER_STACK_PROBE builds.
 */
#define _GNU_SOURCE
#include "critter_common.h"

#include <fcntl.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static const char     *g_unit = "?";
static struct timespec g_t0;

/* ======================================================================== */
/* Sensor model                                                              */
/* ======================================================================== */
static inline uint64_t xs64(uint64_t *s)
{
    uint64_t x = *s;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return *s = x;
}

static inline double u01(uint64_t *s)
{
    return (double)(xs64(s) >> 11) * (1.0 / 9007199254740992.0);
}

void sensor_init(sensor_t *s, uint64_t seed)
{
    s->state = seed ? seed : 0x9E3779B97F4A7C15ULL;
    s->index = 0;
}

double sensor_read_c(sensor_t *s)
{
    const double t = (double)s->index++;
    /* setpoint + compressor cycle (6000 samples) + slow drift */
    double c = 22.0 + 1.5 * sin(6.283185307179586 * t / 6000.0) + 2.0e-6 * t;
    /* sensor noise: approx. gaussian, +/-0.15 C */
    c += (u01(&s->state) + u01(&s->state) + u01(&s->state) - 1.5) * 0.1;
    /* ~0.1% ADC glitches: the outliers the memory unit must remove */
    uint64_t r = xs64(&s->state);
    if ((r & 1023u) == 0) c += ((r >> 10) & 1u) ? 15.0 : -12.0;
    return c;
}

/* ======================================================================== */
/* Arguments                                                                 */
/* ======================================================================== */
const char *arg_str(int argc, char **argv, const char *key, const char *def)
{
    size_t kl = strlen(key);
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (a[0] == '-' && a[1] == '-' && strncmp(a + 2, key, kl) == 0 && a[2 + kl] == '=')
            return a + 3 + kl;
    }
    return def;
}

long arg_long(int argc, char **argv, const char *key, long def)
{
    const char *v = arg_str(argc, argv, key, NULL);
    return v ? strtol(v, NULL, 10) : def;
}

/* ======================================================================== */
/* Tracked heap                                                              */
/* ======================================================================== */
static size_t g_heap_cur, g_heap_peak, g_heap_allocs, g_heap_frees;

static void heap_add(void *p)
{
    if (!p) return;
    g_heap_cur += malloc_usable_size(p);
    if (g_heap_cur > g_heap_peak) g_heap_peak = g_heap_cur;
    g_heap_allocs++;
}

void *cm_malloc(size_t n)
{
    void *p = malloc(n);
    heap_add(p);
    return p;
}

void *cm_calloc(size_t count, size_t n)
{
    void *p = calloc(count, n);
    heap_add(p);
    return p;
}

/* Note: during realloc the old and new blocks can both be live for a moment.
 * Request accounting cannot see that transient; max RSS from time -v can. */
void *cm_realloc(void *old, size_t n)
{
    size_t before = old ? malloc_usable_size(old) : 0;
    void  *p      = realloc(old, n);
    if (!p) return NULL;
    g_heap_cur = g_heap_cur - before + malloc_usable_size(p);
    if (g_heap_cur > g_heap_peak) g_heap_peak = g_heap_cur;
    if (!old) g_heap_allocs++;
    return p;
}

void cm_free(void *p)
{
    if (!p) return;
    g_heap_cur -= malloc_usable_size(p);
    g_heap_frees++;
    free(p);
}

void critter_oom(const char *what, size_t bytes)
{
    printf("@@error=oom\n@@error_detail=%s:%zu\n", what, bytes);
    fflush(stdout);
    fprintf(stderr, "critter[%s]: out of memory allocating %zu bytes for %s\n", g_unit, bytes, what);
    exit(3);
}

void *cm_xmalloc(size_t n, const char *what)
{
    void *p = cm_malloc(n ? n : 1);
    if (!p) critter_oom(what, n);
    return p;
}

/* ======================================================================== */
/* Overlay arena                                                             */
/* ======================================================================== */
int arena_init(arena_t *a, size_t cap)
{
    a->base = (uint8_t *)cm_malloc(cap ? cap : 1);
    a->cap  = cap;
    a->used = a->peak = 0;
    return a->base ? 0 : -1;
}

void *arena_alloc(arena_t *a, size_t n)
{
    size_t off = (a->used + 63u) & ~(size_t)63u; /* cache-line alignment */
    if (off > a->cap || n > a->cap - off) return NULL;
    a->used = off + n;
    if (a->used > a->peak) a->peak = a->used;
    return a->base + off;
}

size_t arena_mark(const arena_t *a) { return a->used; }
void   arena_release(arena_t *a, size_t mark) { a->used = mark; }

void arena_destroy(arena_t *a)
{
    cm_free(a->base);
    a->base = NULL;
    a->cap = a->used = 0;
}

/* ======================================================================== */
/* /proc/self/status without malloc                                          */
/* ======================================================================== */
static char g_status[8192];

static const char *status_read(void)
{
    ssize_t n  = 0;
    int     fd = open("/proc/self/status", O_RDONLY);
    if (fd >= 0) {
        n = read(fd, g_status, sizeof g_status - 1);
        close(fd);
    }
    if (n < 0) n = 0;
    g_status[n] = '\0';
    return g_status;
}

static long status_kb(const char *buf, const char *key)
{
    size_t      kl = strlen(key);
    const char *p  = buf;
    while ((p = strstr(p, key)) != NULL) {
        if ((p == buf || p[-1] == '\n') && p[kl] == ':') return strtol(p + kl + 1, NULL, 10);
        p += kl;
    }
    return -1;
}

static double elapsed_s(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)(t.tv_sec - g_t0.tv_sec) + 1e-9 * (double)(t.tv_nsec - g_t0.tv_nsec);
}

/* ======================================================================== */
/* Stack high-water probe ("stack painting")                                 */
/*   paint: alloca a region below main and fill it with 0xA5                 */
/*   scan : after the workload, count bytes that are no longer 0xA5          */
/* Both are called at the same depth (main -> begin/finish -> paint/scan).   */
/* ======================================================================== */
#ifdef CRITTER_STACK_PROBE
static uintptr_t g_probe_lo, g_probe_hi;

static size_t probe_bytes(void)
{
    const char *e  = getenv("CRITTER_PROBE_KB");
    long        kb = e ? strtol(e, NULL, 10) : 1024;
    if (kb < 64) kb = 64;
    return (size_t)kb * 1024u;
}

__attribute__((noinline)) static void probe_paint(void)
{
    size_t            n = probe_bytes();
    volatile uint8_t *p = (volatile uint8_t *)__builtin_alloca(n);
    for (size_t i = 0; i < n; i++) p[i] = 0xA5;
    g_probe_lo = (uintptr_t)p;
    g_probe_hi = (uintptr_t)p + n;
}

__attribute__((noinline)) static size_t probe_scan(void)
{
    const volatile uint8_t *p = (const volatile uint8_t *)g_probe_lo;
    size_t                  n = g_probe_hi - g_probe_lo, i = 0;
    while (i < n && p[i] == 0xA5) i++;
    return n - i;
}
#endif

void critter_begin(const char *unit)
{
    g_unit = unit;
    clock_gettime(CLOCK_MONOTONIC, &g_t0);
    printf("@@unit=%s\n@@sample_type=%s\n@@sample_bytes=%zu\n", unit, CRITTER_SAMPLE_NAME,
           sizeof(sample_t));
#ifdef CRITTER_STACK_PROBE
    fflush(stdout);
    probe_paint(); /* last thing before the workload so printf frames are not counted */
#endif
}

void critter_phase(const char *name)
{
    const char *b = status_read();
    printf("@@phase=%s vmrss_kb=%ld vmhwm_kb=%ld heap_cur=%zu heap_peak=%zu t_s=%.6f\n", name,
           status_kb(b, "VmRSS"), status_kb(b, "VmHWM"), g_heap_cur, g_heap_peak, elapsed_s());
}

__attribute__((noinline)) static void report_tail(int64_t checksum, long stack_used)
{
    const char *b = status_read();
    printf("@@checksum=%lld\n", (long long)checksum);
    printf("@@runtime_s=%.6f\n", elapsed_s());
    printf("@@heap_peak_bytes=%zu\n@@heap_allocs=%zu\n@@heap_frees=%zu\n@@heap_live_at_exit=%zu\n",
           g_heap_peak, g_heap_allocs, g_heap_frees, g_heap_cur);
    printf("@@vm_peak_kb=%ld\n@@vm_hwm_kb=%ld\n@@vm_rss_kb=%ld\n@@vm_data_kb=%ld\n",
           status_kb(b, "VmPeak"), status_kb(b, "VmHWM"), status_kb(b, "VmRSS"), status_kb(b, "VmData"));
    printf("@@vm_stk_kb=%ld\n@@vm_exe_kb=%ld\n@@vm_lib_kb=%ld\n@@rss_anon_kb=%ld\n@@rss_file_kb=%ld\n",
           status_kb(b, "VmStk"), status_kb(b, "VmExe"), status_kb(b, "VmLib"), status_kb(b, "RssAnon"),
           status_kb(b, "RssFile"));
#if defined(__GLIBC__) && (__GLIBC__ > 2 || (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 33))
    struct mallinfo2 mi = mallinfo2();
    printf("@@malloc_arena_bytes=%zu\n@@malloc_mmap_bytes=%zu\n@@malloc_inuse_bytes=%zu\n", mi.arena,
           mi.hblkhd, mi.uordblks);
#endif
    if (stack_used >= 0) printf("@@stack_hwm_bytes=%ld\n", stack_used);
    fflush(stdout);
}

int critter_finish(int64_t checksum)
{
    long stack_used = -1;
#ifdef CRITTER_STACK_PROBE
    stack_used = (long)probe_scan(); /* first, before any other call dirties the stack */
#endif
    report_tail(checksum, stack_used);
    return 0;
}
