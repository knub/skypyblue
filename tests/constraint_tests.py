from unittest import TestCase
from skypyblue.core import ConstraintSystem
from skypyblue.models import Method, Constraint, Strength

class ConstraintTests(TestCase):

  def setUp(self):
    self.cs = ConstraintSystem()
    self.vars = self.cs.create_variables(["v1", "v2", "v3"], [4, 5, 3])
    self.v1, self.v2, self.v3 = self.vars
    m1_2 = Method(self.v1, self.v2, lambda x: x // 2)
    m1_3 = Method(self.v1, self.v3, lambda x: x // 3)

    self.cn = Constraint(lambda v1, v2, v3: True, Strength.STRONG, self.vars, [m1_3, m1_2])

    self.cs.add_constraint(self.cn)

  def tearDown(self):
    pass


  def test_adding_enforced_to_pplan(self):
    self.assertIsNone(self.cn.mark)

    mark = self.cs.marker.new_mark()
    pplan = self.cn.add_to_pplan([], set(), mark)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_unenforced_to_pplan(self):
    self.cn.selected_method = None
    self.assertIsNone(self.cn.mark)

    pplan = self.cn.add_to_pplan([], set(), self.cs.marker.new_mark())

    self.assertEqual([], pplan)
    self.assertIsNone(self.cn.mark)

  def test_adding_with_the_same_mark(self):

    mark = self.cs.marker.new_mark()
    self.cn.mark = mark
    pplan = self.cn.add_to_pplan([], set(), mark)

    self.assertEqual([], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_with_other_mark(self):

    mark1 = self.cs.marker.new_mark()
    mark2 = self.cs.marker.new_mark()
    self.cn.mark = mark1
    pplan = self.cn.add_to_pplan([], set(), mark2)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark2, self.cn.mark)

