from unittest import TestCase
try:
  from unittest.mock import MagicMock as Mock
except ImportError as e:
  from mock import Mock

from skypyblue.marker import Marker
from skypyblue.models import *
from skypyblue.mvine import Mvine
from skypyblue.constraint_system import ConstraintSystem

marker = Marker()
new_mark = marker.new_mark

class MVineTests(TestCase):

  def setUp(self):
    self.marker = marker;
    self.mvine = Mvine(self.marker)
    self.cs = ConstraintSystem()

  def test_mvine_revoke_cn_fails(self):
    self.mvine.grow = Mock(return_value = False)
    cn = Constraint(None, Strength.WEAKEST, [], [])
    cn.mark = new_mark()

    new_mark()
    not_revoked = self.mvine.revoke_cn(cn, Strength.WEAKEST, [], [])

    self.assertFalse(not_revoked)
    self.assertTrue(cn.mark is None)

  def test_mvine_revoke_cn_succeeds(self):
    self.cs.mvine_grow = Mock(return_value = True)

    cn = Constraint(None, Strength.WEAKEST, [], [])
    v1 = self.cs.create_variable("v1", 1)
    v2 = self.cs.create_variable("v2", 2)
    v3 = self.cs.create_variable("v3", 3)
    for v in [v1,v2,v3]: v.walk_strength = Strength.WEAK

    m = Method([v1, v2], v3, None)
    cn.selected_method = m
    v3.determined_by = m
    redetermined_vars = []

    new_mark()
    not_revoked = self.mvine.revoke_cn(cn, Strength.WEAKEST, [], redetermined_vars)

    self.assertTrue (not_revoked)
    self.assertEqual(Strength.WEAK, v1.walk_strength)
    self.assertEqual(Strength.WEAK, v2.walk_strength)
    self.assertEqual(Strength.WEAKEST, v3.walk_strength)
    self.assertTrue (v3.determined_by is None)
    self.assertTrue (v3 in redetermined_vars)
    self.assertTrue (cn.selected_method is None)

    # case 2 - v3's mark is the same as passed to mvine_revoke_cn

    mark = new_mark()
    cn.selected_method = m
    v3.walk_strength = Strength.WEAK
    v3.determined_by = m
    v3.mark = mark
    redetermined_vars = []
    not_revoked = self.mvine.revoke_cn(cn, Strength.WEAKEST, [], redetermined_vars)

    self.assertTrue (not_revoked)
    self.assertEqual(Strength.WEAK, v1.walk_strength)
    self.assertEqual(Strength.WEAK, v2.walk_strength)
    self.assertEqual(Strength.WEAK, v3.walk_strength)
    self.assertTrue (v3.determined_by is m)
    self.assertTrue (v3 not in redetermined_vars)
    self.assertTrue (cn.selected_method is None)

  # mvine_revoke_cn(cn, Strength.WEAKEST, new_mark(), [], [])
  def test_mvine_grow_with_empty_stack(self):
    new_mark()
    self.assertTrue(self.mvine.grow(Strength.WEAKEST, [], []))

  def test_mvine_grow_with_marked_constraints(self):
    cn1 = Constraint(None, Strength.WEAKEST, [], [])
    cn2 = Constraint(None, Strength.WEAKEST, [], [])
    cn1.mark = new_mark()
    # self.assertTrue(mvine_grow(Strength.WEAKEST, [cn1, cn2], []))

  def test_mvine_grow_with_unmarked_and_weak_constraints(self):
    new_mark()
    cn1 = Constraint(None, Strength.WEAKEST, [], [])
    cn2 = Constraint(None, Strength.WEAKEST, [], [])
    self.mvine.revoke_cn = Mock(return_value = True)
    self.mvine.revoke_cn = Mock(return_value = False)
    stack = [cn2, cn1]
    self.assertFalse(self.mvine.grow(Strength.MEDIUM, stack, []))

  def test_mvine_grow_with_(self):
    cn1 = Constraint(None, Strength.WEAKEST, [], [])
    cn2 = Constraint(None, Strength.REQUIRED, [], [])
    cn1.mark = new_mark()
    self.mvine.enforce_cn = Mock(return_value = False)
    stack = [cn2, cn1]
    self.assertFalse(self.mvine.grow(Strength.MEDIUM, stack, []))


  def test_mvine_enforce_cn_with_no_methods_fails(self):
    cn = Constraint(None, Strength.WEAKEST, [], [])
    cn.mark = new_mark()
    self.mvine.possible_method = Mock(return_value = False)
    new_mark()
    self.assertFalse(self.mvine.enforce_cn(cn, Strength.WEAKEST, [], []))
    self.assertTrue(cn.mark is None)

  def test_mvine_enforce_cn_fails(self):
    v1 = Variable("v1", 1)
    v2 = Variable("v2", 2)
    v3 = Variable("v3", 3)
    m = Method([v1, v2], v3, None)
    cn = Constraint(None, Strength.WEAKEST, [], m)
    cn.mark = new_mark()
    self.mvine.possible_method = Mock(return_value = False)
    new_mark()
    self.assertFalse(self.mvine.enforce_cn(cn, Strength.WEAKEST, [], []))
    self.assertTrue(cn.mark is None)


  # a valid constraint system should not contain method conflicts
  def check_constraint_system(self, constraint_system):
    constrained_variables = set()
    for constraint in constraint_system.constraints:
      if not constraint.is_enforced:
        continue
      for out_var in constraint.selected_method.out_vars:
        if out_var in constrained_variables:
          return False
        constrained_variables.add(out_var)
    return True
