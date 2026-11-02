/*
 * ctime.c - minimal stand-in for GNU `time -v` (used only when GNU time is
 * not installed).  Prints the same field names so one parser handles both.
 *
 * Why a helper at all?  A process's max-RSS high-water mark survives exec(),
 * and a child forked from the (large) Python harness starts life with the
 * harness's RSS.  Measuring through a tiny intermediate process -- exactly
 * what GNU time is -- keeps the harness's memory out of the result.
 *
 *   usage: ctime -o REPORT cmd [args...]
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc < 4 || strcmp(argv[1], "-o") != 0) {
        fprintf(stderr, "usage: %s -o REPORT cmd [args...]\n", argv[0]);
        return 125;
    }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 125; }
    if (pid == 0) {
        execvp(argv[3], argv + 3);
        perror(argv[3]);
        _exit(127);
    }
    int status = 0;
    struct rusage ru;
    if (wait4(pid, &status, 0, &ru) < 0) { perror("wait4"); return 125; }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double el = (double)(t1.tv_sec - t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);

    FILE *f = fopen(argv[2], "w");
    if (!f) { perror(argv[2]); return 125; }
    if (WIFSIGNALED(status)) fprintf(f, "Command terminated by signal %d\n", WTERMSIG(status));
    else if (WEXITSTATUS(status)) fprintf(f, "Command exited with non-zero status %d\n", WEXITSTATUS(status));
    fprintf(f, "\tCommand being timed: \"%s\"\n", argv[3]);
    fprintf(f, "\tUser time (seconds): %.2f\n", ru.ru_utime.tv_sec + ru.ru_utime.tv_usec / 1e6);
    fprintf(f, "\tSystem time (seconds): %.2f\n", ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6);
    fprintf(f, "\tElapsed (wall clock) time (h:mm:ss or m:ss): %d:%05.2f\n", (int)(el / 60), el - 60 * (int)(el / 60));
    fprintf(f, "\tMaximum resident set size (kbytes): %ld\n", ru.ru_maxrss);
    fprintf(f, "\tMajor (requiring I/O) page faults: %ld\n", ru.ru_majflt);
    fprintf(f, "\tMinor (reclaiming a frame) page faults: %ld\n", ru.ru_minflt);
    fprintf(f, "\tVoluntary context switches: %ld\n", ru.ru_nvcsw);
    fprintf(f, "\tInvoluntary context switches: %ld\n", ru.ru_nivcsw);
    fprintf(f, "\tSwaps: %ld\n", ru.ru_nswap);
    fprintf(f, "\tPage size (bytes): %ld\n", sysconf(_SC_PAGESIZE));
    fprintf(f, "\tExit status: %d\n", WIFEXITED(status) ? WEXITSTATUS(status) : 0);
    fclose(f);
    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}
