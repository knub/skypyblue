from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.constraint_system import ConstraintSystem
from skypyblue.mvine import Mvine
from skypyblue.models import *
from fixture import Fixture


class UpdateMethodGraphTests(TestCase):
  
  def setUp(self):
    self.build_mvine = Mvine.build
    Mvine.build = Mock(return_value = True)
    self.cs = ConstraintSystem()
    self.cs.propagate_walk_strength = Mock(return_value = True)
    self.cs.collect_unenforced = Mock(return_value = True)
    self.f = Fixture()

  def tearDown(self):
     Mvine.build = self.build_mvine

  def test_update_method_graph_with_no_constraints(self):
    exec_roots = self.cs.update_method_graph([])
    self.assertEqual(exec_roots, [])

  def test_update_method_graph_with_a_constraint(self):
    self.cs.build_mvine = Mock(return_value = True)
    c = self.f.a_equals_b_plus_2_constraint
    exec_roots = self.cs.update_method_graph([c])
    self.assertEqual(exec_roots, [c])
