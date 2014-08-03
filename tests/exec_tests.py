from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Method, Strength, Variable
from unittest import TestCase, skip

class PplanTests(TestCase):

  def setUp(self):
    self.constraint_system = ConstraintSystem()

  def test_pplan_add_for_one_constraint(self):
    v = Variable("v", 1, self.constraint_system)
    constraint = Constraint(lambda x: x == 5, Strength.STRONG, v, Method([], v, lambda: 5))
    self.constraint_system.add_constraint(constraint)

    self.assertTrue(constraint, v.determined_by)
    self.assertEqual(
      constraint.add_to_pplan([], self.constraint_system.marker.new_mark()),
      [constraint],
      "should contain only the constraint")

  def test_pplan_add_for_two_constraint(self):
    v = Variable("v", 1, self.constraint_system)
    constraint1 = Constraint(lambda x: x == 5, Strength.WEAK, v, Method([], v, lambda: 5))
    constraint2 = Constraint(lambda x: x == 6, Strength.STRONG, v, Method([], v, lambda: 6))
    self.constraint_system.add_constraint(constraint1)
    self.constraint_system.add_constraint(constraint2)

    self.assertFalse(constraint1.is_enforced())
    self.assertTrue(constraint2.is_enforced())
    self.assertTrue(constraint2, v.determined_by)

    self.assertEqual(
      constraint2.add_to_pplan([], self.constraint_system.marker.new_mark()),
      [constraint2],
      "does not add other constraint of \
      a variable if it is not enforced")

    self.assertEqual(
      constraint1.add_to_pplan([], self.constraint_system.marker.new_mark()),
      [],
      "does not add unenforced constraints")

  def test_pplan_add_for_variable(self):
    v = Variable("v", 1, self.constraint_system)
    self.assertEqual(
      v.add_to_pplan([], self.constraint_system.marker.new_mark()),
      [],
      "plain variable return pplan as it was")