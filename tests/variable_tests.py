import unittest
from models.variable import Variable

class VariableTest(unittest.TestCase):
  """
    This only tests basic getters and setters, no constraint solving technology.
  """
  def setUp(self):
    self.variable = Variable("variable",10)

  def test_get_and_set_variable(self):
    self.assertEqual(self.variable.get_value(), 10)
    self.variable.set_value(5)
    self.assertEqual(5, self.variable.get_value())