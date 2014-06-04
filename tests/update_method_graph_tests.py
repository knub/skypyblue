from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.constraint_system import ConstraintSystem, max_out
from skypyblue.models import *

new_mark = ConstraintSystem().new_mark

class UpdateMethodGraphTests(TestCase):
  
  def setUp(self):
    self.cs = ConstraintSystem()

  def test_update_method_graph(self):
    self.cs.build_mvine = Mock(return_value = True)
    exec_roots = self.cs.update_method_graph([])
    self.assertEqual(exec_roots, [])

