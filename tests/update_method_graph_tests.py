from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.core import ConstraintSystem, Mvine
from skypyblue.models import *
from fixture import Fixture

class UpdateMethodGraphTests(TestCase):

  def setUp(self):
    self.build_mvine = Mvine.build
    Mvine.build = Mock(return_value = True)
    self.cs = ConstraintSystem()
    self.cs._propagate_walk_strength = Mock(return_value = True)
    self.cs.collect_unenforced = Mock(return_value = True)
    self.f = Fixture()

  def tearDown(self):
     Mvine.build = self.build_mvine

  def test_update_method_graph_with_no_constraints(self):
    self.cs._update_method_graph()
    self.assertEqual([], self.cs.exec_roots)

  def test_update_method_graph_with_a_constraint(self):
    self.cs.build_mvine = Mock(return_value = True)
    c = self.f.a_equals_b_plus_2_constraint
    self.cs.unenforced_constraints.add(c)
    self.cs._update_method_graph()
    self.assertEqual([c], self.cs.exec_roots)
