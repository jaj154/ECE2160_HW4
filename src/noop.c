/*
 * noop.c - the process floor.  An empty Critter program: C runtime, libc,
 * dynamic loader and the instrumentation itself.  Every other measurement
 * includes this cost, so it is the zero-point for interpreting results.
 */
#include "critter_common.h"

int main(void)
{
    critter_begin("noop");
    return critter_finish(0);
}
