from unittest import TestCase
from skypyblue.models import *
from skypyblue.core import Mvine, Marker, ConstraintSystem

class ChainTests(TestCase):

  def setUp(self):
    cs = ConstraintSystem()
    self.first = None
    self.last = None
    prev = None
    n = 50
    # We need to go up to n inclusively, as this is done
    # in the original test as well
    for i in range(n + 1):
      name = "v%s" % i
      v = Variable(name, 0, cs)

      if prev is not None:
        c = ConstraintFactory.equality_constraint(prev, v, Strength.STRONG)
        cs.add_constraint(c)
      if i == 0:
        self.first = v

      if i == n:
        self.last = v

      prev = v

    self.last.stay()

  def test_chain_of_constraints(self):
    self.first.set_value(5)
    self.assertEqual(5,self.last.get_value())
