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

    self.selected_method = None
    self.mark = None

  def add_to_pplan(self, pplan, done_mark):
    stack = [self]
    while stack:
      cur_cn = stack.pop()
      if cur_cn.selected_method is None or cur_cn.mark == done_mark:
        continue
      cur_cn.mark = done_mark
      pplan.insert(0, cur_cn)
      for var in cur_cn.selected_method.outputs:
        for var_cn in var.constraints:
          if var_cn != var.determined_by:
            stack.append(var_cn)
    return pplan


  def is_enforced(self):
    "returns True is there is is a method selected, otherwise False"
    return self.selected_method is not None

  def __str__(self):
    return "<Constraint %s>" % (
      inspect.getsource(self.check_function).strip().strip(","))

  def __repr__(self):
    return str(self)
