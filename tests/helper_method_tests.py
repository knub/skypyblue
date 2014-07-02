from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.core import ConstraintSystem, Marker
from skypyblue.models import *

new_mark = Marker().new_mark


class HelperTests(TestCase):

  def test_max_out(self):
    cs = ConstraintSystem()
    v1 = Variable("v1", 13, cs)
    v2 = Variable("v2", 12, cs)
    method = Method(v1, v2, lambda v1: v1 - 1)

    self.assertEqual(Strength.WEAKEST, cs.max_out(method, [v1]))

  def test_new_mark_are_numbers(self):
    used_marks = set()
    for i in range(100):
      mark  = new_mark()
      self.assertTrue(mark not in used_marks)
      used_marks.add(mark)
