import unittest, sys
sys.path.append("../../src")

from skypyblue.constraint_system import *

"""
See deltablue_test#chain_test for documentation
on this benchmark.
"""
def chain_test(n):
  cs = ConstraintSystem()
  cf = models.ConstraintFactory()
  prev, first, last = None, None, None

  # We need to go up to n inclusively.
  for i in range(n + 1):
    name = "v%s" % i
    v = Variable(name, 0, cs)

    if prev is not None:
      c = cf.equality_constraint(prev, v, Strength.REQUIRED)
      cs.add_constraint(c)
    if i == 0:
      first = v

    if i == n:
      last = v

    prev = v

  cs.stay(last, Strength.MEDIUM)

  for i in range(100):
    first.set_value(i)

    if last.get_value != i:
      print("Chain test failed.")

def skypyblue(innerIter):
  chain_test(innerIter)

