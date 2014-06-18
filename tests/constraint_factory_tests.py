import unittest
from skypyblue.core import ConstraintSystem
from skypyblue.models import ConstraintFactory, Strength

class ConstraintFactoryTestClass(unittest.TestCase):
  
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

    self.assertTrue(variable1.get_value()==variable2.get_value())

  def test_scale_constraint(self):
    destination = self.constraint_system.create_variable("destination",1)
    source = self.constraint_system.create_variable("source",2)
    scale = self.constraint_system.create_variable("scale",3)
    offset = self.constraint_system.create_variable("offset",4)

    constraint = self.constraint_factory.scale_constraint(
        destination,
        source,
        scale,
        offset,
        Strength.STRONG
      )

    self.constraint_system.add_constraint(constraint)

    self.assertTrue(destination.get_value()==scale.get_value()*source.get_value()+offset.get_value())
    destination.set_value(100)
    self.assertTrue(destination.get_value()==scale.get_value()*source.get_value()+offset.get_value())

