#!/usr/bin/env python3
import sys, os

try:
  from termcolor import colored, cprint
except:
  def cprint(s, attrs):
    print(s)

from deltablue_test import *
from skypyblue_test import *


def benchmark(constraint_solver):
  for i in range(warmUp):
    constraint_solver()

  for i in range(numIterations):
    startTime = time.time()
    constraint_solver()
    endTime = time.time()
    milliseconds = int((endTime - startTime) * 1000)
    print("iterations=%d runtime: %dms" % (i, milliseconds))

if len(sys.argv) < 4:
  numIterations = 10
  warmUp        = 10
  innerIter     = 1000
  print("Not all parameters specified. Using default parameters " +
    "n: %d warm: %d constraints: %d" %
    (numIterations, warmUp, innerIter))
else:
  # outer iterations
  numIterations = int(sys.argv[1])
  # outer warmup iterations
  warmUp        = int(sys.argv[2])
  # test size
  innerIter     = int(sys.argv[3])

print()
cprint("Deltablue results", attrs = ['bold'])
cprint("================================", attrs = ['bold'])
benchmark(lambda: delta_blue(innerIter))

cprint("Skypyblue results", attrs = ['bold'])
cprint("================================", attrs = ['bold'])
benchmark(lambda: skypyblue(innerIter))
