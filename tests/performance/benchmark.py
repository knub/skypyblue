#!/usr/bin/env python3
import sys, os, time

try:
  from termcolor import colored, cprint
except:
  def cprint(s, attrs):
    print(s)

from deltablue_test import *
from skypyblue_test import *


def benchmark(constraint_solver, warmUp, numIterations):
  for i in range(warmUp):
    constraint_solver()

  for i in range(numIterations):
    startTime = time.time()
    constraint_solver()
    endTime = time.time()
    milliseconds = int((endTime - startTime) * 1000)
    print("iterations=%d runtime: %dms" % (i, milliseconds))

def run_benchmark(args):
  if len(args) < 3:
    numIterations = 5
    warmUp        = 5
    innerIter     = 100
    print("Not all parameters specified. Using default parameters " +
      "n: %d warm: %d constraints: %d" %
      (numIterations, warmUp, innerIter))
  else:
    # outer iterations
    numIterations = int(args[0])
    # outer warmup iterations
    warmUp        = int(args[1])
    # test size
    innerIter     = int(args[2])

  cprint("Deltablue results", attrs = ['bold'])
  cprint("================================", attrs = ['bold'])
  benchmark(lambda: delta_blue(innerIter), warmUp, numIterations)

  cprint("Skypyblue results", attrs = ['bold'])
  cprint("================================", attrs = ['bold'])
  benchmark(lambda: skypyblue(innerIter), warmUp, numIterations)

if __name__ == "__main__":
  run_benchmark(sys.argv[1:])
