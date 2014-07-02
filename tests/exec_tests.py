from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Method, Strength, Variable
from unittest import TestCase, skip

class PplanTests(TestCase):

  def setUp(self):
    self.cs = ConstraintSystem()

  def test_pplan_add_for_one_constraint(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)

    self.assertTrue(cn, v.determined_by)
    self.assertEqual(
      cn.add_to_pplan([], self.cs.marker.new_mark()),
      [cn],
      "should contain only the constraint")

  def test_pplan_add_for_two_constraint(self):
    v = Variable("v", 1, self.cs)
    cn1 = Constraint(lambda x: x == 5, Strength.WEAK, v, Method([], v, lambda: 5))
    cn2 = Constraint(lambda x: x == 6, Strength.STRONG, v, Method([], v, lambda: 6))
    self.cs.add_constraint(cn1)
    self.cs.add_constraint(cn2)

    self.assertFalse(cn1.is_enforced())
    self.assertTrue(cn2.is_enforced())
    self.assertTrue(cn2, v.determined_by)

    self.assertEqual(
      cn2.add_to_pplan([], self.cs.marker.new_mark()),
      [cn2],
      "does not add other constraint of \
      a variable if it is not enforced")

    self.assertEqual(
      cn1.add_to_pplan([], self.cs.marker.new_mark()),
      [],
      "does not add unenforced constraints")

  def test_pplan_add_for_variable(self):
    v = Variable("v", 1, self.cs)
    self.assertEqual(
      v.add_to_pplan([], self.cs.marker.new_mark()),
      [],
      "plain variable return pplan as it was")


class ExecFromRootTests(TestCase):

  def setUp(self):
    self.cs = ConstraintSystem()

  def test_exec_pplan_create_with_empty_input(self):
    pplan = self.cs.exec_pplan_create()
    self.assertEqual([], pplan)

  def test_exec_pplan_create_with_one_cn(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)
    self.cs.exec_roots = [cn]
    self.assertEqual([cn], self.cs.exec_pplan_create())

  def test_exec_pplan_create_with_one_unmarked_cn(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)
    self.cs.exec_roots = [cn]
    self.assertEqual([cn], self.cs.exec_pplan_create())

  def test_exec_pplan_create_with_one_marked_cn(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)
    cn.mark = self.cs.mark
    self.cs.exec_roots = [cn]
    self.assertEqual([], self.cs.exec_pplan_create())

  @skip("Broken test.")
  def test_exec_pplan_create_with_one_undetermined_var(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)
    v.determined_by = None
    self.cs.exec_roots = [v]
    self.assertEqual([cn], self.cs.exec_pplan_create())

  def test_exec_pplan_create_with_one_determined_var(self):
    v = Variable("v", 1, self.cs)
    cn = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.cs.add_constraint(cn)
    self.cs.exec_roots = [v]
    self.assertEqual([], self.cs.exec_pplan_create())
