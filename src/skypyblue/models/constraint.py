import inspect
class Constraint:
  def __init__(self, check_function, strength, variables, methods):
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

  def add_to_pplan(self, pplan, done_mark):
    if self.is_enforced() and self.mark != done_mark:
      self.mark = done_mark
      for var in self.selected_method.outputs:
        var.add_to_pplan(pplan, done_mark)
      if self not in pplan:
        pplan.append(self)
    return pplan

  def is_enforced(self):
    "returns True is there is is a method selected, otherwise False"
    return not self.selected_method is None

  def __str__(self):
    return "<Constraint check: %s>" % (
      inspect.getsource(self.check_function).strip())

  def __repr__(self):
    return str(self)

  def add_valid_plan(self, plan):
    self.valid_plans.append(plan)

  def invalidate_plans(self):
    for plan in self.valid_plans:
      plan.valid = False
      for constraint in set(plan.root_constraints+plan.good_constraints+plan.bad_constraints):
        if self != constraint:
          self.valid_plans.remove(plan)

    self.valid_plans.clear()

  def invalidate_plans_on_setting_method(self, method):
    self.invalidate_plans()
    if method != None:
      for var in method.inputs:
        if var.determined_by != None:
          var.determined_by.invalidate_plans()

  @property
  def selected_method(self):
    return self._selected_method

  @selected_method.setter 
  def selected_method(self,method):
    self._selected_method = method
    self.invalidate_plans_on_setting_method(method)




