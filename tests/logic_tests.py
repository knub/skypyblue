from unittest import TestCase
from logic import *
from models import *
   

class HelperTests(TestCase):

  def test_max_out(self):
    v1 = Variable("v1", 13)
    v2 = Variable("v2", 12)
    method = Method(v1, v2, lambda v1: v1-1)

    # any other scenarios, where it is not WEAKEST???
    self.assertEqual(Strength.WEAKEST, max_out(method, [v1]))

  def test_new_mark_are_numbers(self):
    start = new_mark() + 1
    for i in range(start, start + 100):
      self.assertEqual(i, new_mark(), "marks should be increasing numbers")
