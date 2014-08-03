from skypyblue.models import Constraint

class Plan(object):
  def __init__(self, root_constraints, good_constraints, bad_constraints, valid):
    """
    root_constraints    constraints used to construct this plan
    good_constraints    ordered list of enforced constraints in plan
    bad_constraints     enforced constraints in and downstream of cycles
    valid:              true if this plan is valid
    """
    self.root_constraints = root_constraints
    self.good_constraints = good_constraints
    self.bad_constraints = bad_constraints
    self.valid = valid
    constraints = self.root_constraints + self.good_constraints + self.bad_constraints
    for constraint in constraints:
        constraint.add_valid_plan(self)
