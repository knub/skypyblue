from unittest import TestCase
from unittest.mock import MagicMock

from logic import *
import logic
from models import *
# Test ideas:
# - when a stable constraint system is executed multiple times, the results
#   stay the same (idempotence)

class HelperTests(TestCase):

  def test_max_out(self):
    v1 = Variable("v1", 13)
    v2 = Variable("v2", 12)
    method = Method(v1, v2, lambda v1: v1-1)

    # any other scenarios, where it is not WEAKEST???
    self.assertEqual(Strength.WEAKEST, max_out(method, [v1]))

  def test_new_mark_are_numbers(self):
    used_marks = set()
    for i in range(100):
      mark  = new_mark()
      self.assertTrue(mark not in used_marks)
      used_marks.add(mark)

class MVineTests(TestCase):
  def test_mvine_revoke_cn(self):
    cn = Constraint(None, Strength.WEAKEST, [], [])
    cn.mark = new_mark()
    logic.mvine_grow = MagicMock(return_value = False)
    not_revoked = mvine_revoke_cn(cn, Strength.WEAKEST, new_mark(), [], [])
    self.assertFalse(not_revoked)
    self.assertTrue(cn.mark is None)

    logic.mvine_grow = MagicMock(return_value = True)
    cn = Constraint(None, Strength.WEAKEST, [], [])
    v1 = Variable("v1", 1, Strength.WEAK)
    v2 = Variable("v2", 2, Strength.WEAK)
    v3 = Variable("v3", 3, Strength.WEAK)
    cn.selected_method = Method([v1, v2], v3, None)
    

  # mvine_revoke_cn(cn, Strength.WEAKEST, new_mark(), [], [])

    
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
