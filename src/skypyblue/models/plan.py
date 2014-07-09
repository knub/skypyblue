from skypyblue.models import Constraint

class Plan:
  def __init__(self, root_constraints, good_constraints, bad_constraints, valid):
    """
    root_constraints \tconstraints used to construct this plan
    good_constraints \t ordered list of enforced constraints in plan
    bad_constraints \t enforced constraints in and downstream of cycles
    valid:\ttrue if this plan is valid
    """
    self.root_constraints = root_constraints
    self.good_constraints = good_constraints
    self.bad_constraints = bad_constraints
    self.valid = valid

    for cn in self.root_constraints.union(self.good_constraints).union(self.bad_constraints):
      if isinstance(cn, Constraint):
        cn.add_valid_plan(self)
