#!/usr/bin/env python3
import sys
from termcolor import colored, cprint

from deltablue_test import *
from skypyblue_test import *
 
if len(sys.argv) < 4:
  print("Not all parameters specified. Using default parameters 5 5 2000")
  numIterations = 5
  warmUp        = 5
  innerIter     = 2000
else:
  # outer iterations
  numIterations = int(sys.argv[1])
  # outer warmup iterations
  warmUp        = int(sys.argv[2])
  # test size
  innerIter     = int(sys.argv[3])

print()
cprint("Delta-Blue results", attrs = ['bold'])
cprint("================================", attrs = ['bold'])
for i in range(warmUp):
  startTime, endTime = delta_blue(innerIter)

for i in range(numIterations):
  startTime, endTime = delta_blue(innerIter)
  milliseconds = int((endTime - startTime) * 1000)
  print("DeltaBlue: iterations=%d runtime: %dms" % (i, milliseconds))



cprint("Skypyblue results", attrs = ['bold'])
cprint("================================", attrs = ['bold'])
