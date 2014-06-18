import unittest, sys
sys.path.append("../../src")

from skypyblue.core import *
from skypyblue import *
from skypyblue.models import *

"""
See deltablue_test#chain_test for documentation
on this benchmark.
Basic structure
v1 -> v2 -> v3 -> v4 ... -> vn
"""
def chain_test(n):
  cs = ConstraintSystem()
  cf = ConstraintFactory()
  prev, first, last = None, None, None

  # We need to go up to n inclusively, as this is done
  # in the original test as well
  for i in range(n + 1):
    name = "v%s" % i
    v = Variable(name, 0, cs)

    if prev is not None:
      c = cf.equality_constraint(prev, v, Strength.STRONG)
      cs.add_constraint(c)
    if i == 0:
      first = v

    if i == n:
      last = v

    prev = v

  cs.add_stay_constraint(last, Strength.MEDIUM)

  for i in range(100):
    first.set_value(i)

    if last.get_value() != i:
      print("Chain test failed.")

"""
See deltablue_test#projection_test for documentation
on this benchmark.
Basic structure
v1 -> v2
v3 -> v4
v5 -> v6
...
"""
def projection_test(n):
  cs = ConstraintSystem()
  cf = ConstraintFactory()
  scale = Variable("scale", 10, cs)
  offset = Variable("offset", 1000, cs)
  src, dest = None, None
  dests = []
  for i in range(n):
    src = Variable("src%s" % i, i)
    dst = Variable("dst%s" % i, i)
    dests.append(dst)
    cs.add_stay_constraint(src)
    cf.scale_constraint(dest, src, scale, offset, Strength.STRONG)

  src.set_value(17)
  if dst.value != 1170:
    print("Projection 1 failed")

def skypyblue(innerIter):
  chain_test(innerIter)
  projection_test(innerIter)

