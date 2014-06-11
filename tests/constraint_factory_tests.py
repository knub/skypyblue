import unittest
from skypyblue.core import ConstraintSystem
from skypyblue.models import ConstraintFactory

class ConstraintFactoryTestClass:
  
  __name__ = "ConstraintFactoryTestClass"

  def setUp(self):
    self.constraint_factory = ConstraintFactory()
    self.constraint_system = ConstraintSystem()

  def test_equality_constraint(self):
    variable1 = self.constraint_system.create_variable("variable1",10)
    variable2 = self.constraint_system.create_variable("variable2",20)

    constraint = self.constraint_factory.equality_constraint(
        variable1,
        variable2,
        Strength.STRONG
      )

    self.constraint_system.add_constraint(constraint)

    self.assertTrue(variable1.getValue()==variable2.getValue())

