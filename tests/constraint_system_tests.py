import unittest
from constraint_system import ConstraintSystem
from models.constraint import Constraint
from models.strengths import Strength

class ConstraintSystemTest(unittest.TestCase):
  """
    This only tests basic getters and setters, no constraint solving technology.
  """
  def setUp(self):
    self.cs = ConstraintSystem()
    self.v1 = self.cs.create_variable("v1", 15)
    self.c1 = Constraint(lambda x: True, Strength.REQUIRED, [self.v1], [])

  def test_create_variable(self):
    self.assertTrue(self.v1 in self.cs.variables)

  def test_variable_constraints_is_set_after_add_constraint(self):
    self.cs.add_constraint(self.c1)
    self.assertTrue(self.c1 in self.v1.constraints)

  def test_variable_constraints_is_set_after_remove_constraint(self):
    self.cs.add_constraint(self.c1)
    self.cs.remove_constraint(self.c1)
    self.assertEqual([], self.v1.constraints)
