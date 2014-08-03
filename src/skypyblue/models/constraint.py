import inspect
from skypyblue.core import logger


class Constraint(object):
  def __init__(self, check_function, strength, variables, methods, name = ""):
    """
    check_function: is lambda returning bool. defines a contraint and can be used to check, whether the contraint is fullfilled
    strength:       is of type skypyblue.models.strength.Strength and indicates how important it is to fullfill the contraint
    variables:      list of skypyblue.models.variables.Variable that are involved in the contraint
    methods:        list of skypyblue.models.methods.Method that can fullfill a contraint

    Usage:
      c = Constraint(
        lambda v1, v2: v1 < v2,
        Strength.STRONG,
        [v1, v2],
        [some_method])
    """
    self.check_function = check_function
    self.strength = strength
    self.variables = variables if isinstance(variables, list) else [variables]
    self.methods = methods if isinstance(methods, list) else [methods]

    self._selected_method = None
    self.valid_plans = []
    self.mark = None
    self.name = name

  def add_to_pplan(self, pplan, done_mark):
    insert_index = len(pplan)
    stack = [self]
    while stack:
      current_constraint = stack.pop()
      if current_constraint.selected_method is None or current_constraint.mark == done_mark:
        continue
      current_constraint.mark = done_mark
      pplan.insert(insert_index, current_constraint)
      for variable in current_constraint.selected_method.outputs:
        for constraint in variable.constraints:
          if constraint != variable.determined_by:
            stack.append(constraint)
    return pplan

  def is_enforced(self):
    "returns True is there is is a method selected, otherwise False"
    return self.selected_method is not None

  def __str__(self):
    if self.name:
      return "<Constraint '%s'>" % (self.name)
    else:
      return "<Constraint %s>" % (
        inspect.getsource(self.check_function).strip().strip(","))

  def __repr__(self):
    return str(self)

  def add_valid_plan(self, plan):
    self.valid_plans.append(plan)

  def invalidate_plans(self):
    for plan in self.valid_plans:
      plan.valid = False
      for constraint in plan.root_constraints + plan.good_constraints + plan.bad_constraints:
        if self != constraint:
          if plan in constraint.valid_plans:
            constraint.valid_plans.remove(plan)

    self.valid_plans = []

  def invalidate_plans_on_setting_method(self):
    self.invalidate_plans()
    if self._selected_method != None:
      for variable in self._selected_method.inputs:
        if variable.determined_by != None:
          variable.determined_by.invalidate_plans()

  @property
  def selected_method(self):
    return self._selected_method

  @selected_method.setter
  def selected_method(self, method):
    self._selected_method = method
    self.invalidate_plans_on_setting_method()