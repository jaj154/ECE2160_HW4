/*
 * smapsdump.c - LD_PRELOAD helper used only for the FORTIFY investigation.
 * At process exit it copies /proc/self/smaps and /proc/self/status to
 * $CRITTER_SMAPS_OUT, so two builds can be compared mapping by mapping.
 *   gcc -shared -fPIC -O2 tools/smapsdump.c -o smapsdump.so
 *   CRITTER_SMAPS_OUT=out.txt LD_PRELOAD=./smapsdump.so ./io --n=20000
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

static void copy(int out, const char *path, const char *banner, size_t blen)
{
    char buf[8192];
    int in = open(path, O_RDONLY);
    if (in < 0) return;
    if (write(out, banner, blen) < 0) { close(in); return; }
    ssize_t n;
    while ((n = read(in, buf, sizeof buf)) > 0)
        if (write(out, buf, (size_t)n) != n) break;
    close(in);
}

__attribute__((destructor)) static void dump(void)
{
    const char *p = getenv("CRITTER_SMAPS_OUT");
    if (!p) return;
    int out = open(p, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (out < 0) return;
    copy(out, "/proc/self/status", "### status\n", 11);
    copy(out, "/proc/self/smaps", "### smaps\n", 10);
    close(out);
}
