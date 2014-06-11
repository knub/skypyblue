import unittest
from skypyblue.models import Variable, Strength

try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

class VariableTest(unittest.TestCase):
  """
    This only tests basic getters and setters, no constraint solving technology.
  """
  def setUp(self):
    self.variable = Variable("variable", 10)
    self.variable.system = Mock()
    self.variable.system.remove_constraint = Mock()
    self.variable.system.add_stay_constraint = Mock()

  def test_get_and_set_variable(self):
    self.assertEqual(self.variable.get_value(), 10)
    self.variable.set_value(5)
    self.assertEqual(5, self.variable.get_value())

  def test_stay(self):
    self.assertTrue(self.variable.stay_constraint is None)
    self.variable.stay()
    self.assertFalse(self.variable.stay_constraint is None)
    self.variable.system.add_stay_constraint.assert_called_with(self.variable,Strength.WEAK)

  def test_stay_tow_times(self):
    self.variable.stay()
    self.assertFalse(self.variable.system.remove_constraint.called)
    self.variable.stay(Strength.STRONG)
    self.assertTrue(self.variable.system.remove_constraint.called)
    self.variable.system.add_stay_constraint.assert_called_with(self.variable,Strength.STRONG)
