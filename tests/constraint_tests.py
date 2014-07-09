from unittest import TestCase
from skypyblue.core import ConstraintSystem, logger
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
    pplan = self.cn.add_to_pplan([], mark)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_unenforced_to_pplan(self):
    self.cn.selected_method = None
    self.assertIsNone(self.cn.mark)

    pplan = self.cn.add_to_pplan([], self.cs.marker.new_mark())

    self.assertEqual([], pplan)
    self.assertIsNone(self.cn.mark)

  def test_adding_with_the_same_mark(self):

    mark = self.cs.marker.new_mark()
    self.cn.mark = mark
    pplan = self.cn.add_to_pplan([], mark)

    self.assertEqual([], pplan)
    self.assertEqual(mark, self.cn.mark)

  def test_adding_with_other_mark(self):

    mark1 = self.cs.marker.new_mark()
    mark2 = self.cs.marker.new_mark()
    self.cn.mark = mark1
    pplan = self.cn.add_to_pplan([], mark2)

    self.assertEqual([self.cn], pplan)
    self.assertEqual(mark2, self.cn.mark)


  # def test_adding_iterative_should_be_in_the_right_order(self):
  #   cs = ConstraintSystem()

  #   all_vars = cs.create_variables(["a", "b", "c"], [1, 2, 3])
  #   a, b, c = all_vars

  #   m1 = Method([a, c], [b], lambda a,c: a + c)
  #   m2 = Method([b, c], [a], lambda b,c: b - c)

  #   cn = Constraint(lambda a,b,c: a + c == b, Strength.STRONG, [a, b, c], [m1, m2], "cn1")

  #   self.cs.add_constraint(cn)

  #   a.stay()
  #   a_stay_cn = a.stay_constraint

  #   c.set_value(8)
  #   c_set_cn = cs.forced_constraint

  #   cs.exec_roots = [c_set_cn, a_stay_cn]
  #   self.assertEqual([cn, c_set_cn, a_stay_cn], cs.exec_pplan_create())
