import unittest
from skypyblue.core import ConstraintSystem
from skypyblue.models import ConstraintFactory, Strength, Variable

class ConstraintFactoryTestClass(unittest.TestCase):
  
  __name__ = "ConstraintFactoryTestClass"

  def setUp(self):
    self.constraint_system = ConstraintSystem()

  def test_equality_constraint(self):
    variable1 = Variable("variable1", 10, self.constraint_system)
    variable2 = Variable("variable2", 20, self.constraint_system)

    constraint = ConstraintFactory.equality_constraint(
        variable1,
        variable2,
        Strength.STRONG
      )

    self.constraint_system.add_constraint(constraint)

    self.assertTrue(variable1.get_value()==variable2.get_value())

  def test_scale_constraint(self):
    destination = Variable("destination", 1, self.constraint_system)
    source = Variable("source", 2, self.constraint_system)
    scale = Variable("scale", 3, self.constraint_system)
    offset = Variable("offset", 4, self.constraint_system)

    constraint = ConstraintFactory.scale_constraint(
        destination,
        source,
        scale,
        offset,
        Strength.STRONG
      )

    self.constraint_system.add_constraint(constraint)

    self.assertTrue(destination.get_value() == scale.get_value() * source.get_value() + offset.get_value())
    destination.set_value(100)
    self.assertTrue(destination.get_value() == scale.get_value() * source.get_value() + offset.get_value())