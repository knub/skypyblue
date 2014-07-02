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
  prev, first, last = None, None, None

  # We need to go up to n inclusively, as this is done
  # in the original test as well
  for i in range(n + 1):
    name = "v%s" % i
    v = Variable(name, 0, cs)

    if prev is not None:
      c = ConstraintFactory.equality_constraint(prev, v, Strength.STRONG)
      cs.add_constraint(c)
    if i == 0:
      first = v

    if i == n:
      last = v

    prev = v

  last.stay()

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
  scale = Variable("scale", 10, cs)
  offset = Variable("offset", 1000, cs)
  src, dest = None, None
  dests = []
  for i in range(n):
    src = Variable("src%s" % i, i, cs)
    dest = Variable("dest%s" % i, i, cs)
    dests.append(dest)
    src.stay()
    c = ConstraintFactory.scale_constraint(dest, src, scale, offset, Strength.STRONG)
    cs.add_constraint(c)

  src.set_value(17)
  if dest.get_value() != 1170:
    print("Projection 1 failed")

  dest.set_value(1050)
  if src.get_value() != 5:
    print("Projection 2 failed")

  scale.set_value(5)

  for i in range(n - 1):
    if dests[i].get_value() != (i * 5 + 1000):
      print("Projection 3 failed")

  offset.set_value(2000)

  for i in range(n - 1):
    if dests[i].get_value() != (i * 5 + 2000):
      print("Projection 4 failed")

def skypyblue(innerIter):
  chain_test(innerIter)
  projection_test(innerIter)

