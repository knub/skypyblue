from unittest import TestCase
from skypyblue.core import ConstraintSystem, logger
from skypyblue.models import Method, Constraint, Strength

class ConstraintTests(TestCase):

  def setUp(self):
    self.constraint_system = ConstraintSystem()
    self.variables = self.constraint_system.create_variables(["v1", "v2", "v3"], [4, 5, 3])
    self.v1, self.v2, self.v3 = self.variables
    method1_2 = Method(self.v1, self.v2, lambda x: x // 2)
    method1_3 = Method(self.v1, self.v3, lambda x: x // 3)

    self.constraint = Constraint(lambda v1, v2, v3: True, Strength.STRONG, self.variables, [method1_3, method1_2])

    self.constraint_system.add_constraint(self.constraint)

  def tearDown(self):
    pass


  def test_adding_enforced_to_pplan(self):
    self.assertIsNone(self.constraint.mark)

    mark = self.constraint_system.marker.new_mark()
    pplan = self.constraint.add_to_pplan([], mark)

    self.assertEqual([self.constraint], pplan)
    self.assertEqual(mark, self.constraint.mark)

  def test_adding_unenforced_to_pplan(self):
    self.constraint.selected_method = None
    self.assertIsNone(self.constraint.mark)

    pplan = self.constraint.add_to_pplan([], self.constraint_system.marker.new_mark())

    self.assertEqual([], pplan)
    self.assertIsNone(self.constraint.mark)

  def test_adding_with_the_same_mark(self):

    mark = self.constraint_system.marker.new_mark()
    self.constraint.mark = mark
    pplan = self.constraint.add_to_pplan([], mark)

    self.assertEqual([], pplan)
    self.assertEqual(mark, self.constraint.mark)

  def test_adding_with_other_mark(self):

    mark1 = self.constraint_system.marker.new_mark()
    mark2 = self.constraint_system.marker.new_mark()
    self.constraint.mark = mark1
    pplan = self.constraint.add_to_pplan([], mark2)

    self.assertEqual([self.constraint], pplan)
    self.assertEqual(mark2, self.constraint.mark)

