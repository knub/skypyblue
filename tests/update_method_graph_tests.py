from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.constraint_system import ConstraintSystem
from skypyblue.mvine import Mvine
from skypyblue.models import *


class UpdateMethodGraphTests(TestCase):
  
  def setUp(self):
    self.build_mvine = Mvine.build
    Mvine.build = Mock(return_value = True)
    self.cs = ConstraintSystem()

  def tearDown(self):
     Mvine.build = self.build_mvine

  def test_update_method_graph(self):
    exec_roots = self.cs.update_method_graph([])
    self.assertEqual(exec_roots, [])

