"""Critter Memory Lab: a test harness for embedded memory optimisation.

Modules
  env        platform probing (page size, compiler, libc, GNU time)
  build      compile one binary per configuration, read image/stack sizes
  runner     run under /usr/bin/time -v, parse, repeat, aggregate
  testcases  every experiment declared as data (add yours here)
  analysis   noise-aware REDUCES / INCREASES / NEUTRAL classification
  report     terminal output and log files
  core       orchestration
"""
__version__ = "1.0.0"
