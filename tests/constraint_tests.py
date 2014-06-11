from unittest import TestCase
from skypyblue.core import ConstraintSystem
from skypyblue.models import Method, Constraint, Strength
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

class ConstraintTests(TestCase):

  def setUp(self):
    self.cs = ConstraintSystem()
    self.vars = self.cs.create_variables(["v1", "v2", "v3"], [4,5,3])
    self.v1, self.v2, self.v3 = self.vars
    m1_2 = Method(self.v1, self.v2, lambda x: x // 2)
    m1_3 = Method(self.v1, self.v3, lambda x: x // 3)

    self.cn = Constraint(lambda: True, Strength.STRONG, self.vars, [m1_3, m1_2])

    self.cs.add_constraint(self.cn)

  def tearDown(self):
    pass


  def test_adding_enforced_to_pplan(self):
    self.cn.is_enforced = Mock(return_value = True)
    self.assertIsNone(self.cn.mark)

    mark = self.cs.marker.new_mark()
    pplan = self.cn.add_to_pplan([], mark)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_unenforced_to_pplan(self):
    self.cn.is_enforced = Mock(return_value = False)
    self.assertIsNone(self.cn.mark)

    pplan = self.cn.add_to_pplan([], self.cs.marker.new_mark())

    self.assertEqual([], pplan)
    self.assertIsNone(self.cn.mark)

  def test_adding_with_the_same_mark(self):
    self.cn.is_enforced = Mock(return_value = True)

    mark = self.cs.marker.new_mark()
    self.cn.mark = mark
    pplan = self.cn.add_to_pplan([], mark)

    self.assertEqual([], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_with_other_mark(self):
    self.cn.is_enforced = Mock(return_value = True)

    mark1 = self.cs.marker.new_mark()
    mark2 = self.cs.marker.new_mark()
    self.cn.mark = mark1
    pplan = self.cn.add_to_pplan([], mark2)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark2, self.cn.mark)

