

class CycleException(Exception):
  """Constraint system raises this exception, if a cycle was detected"""
  def __init__(self, cycle = set(), message = "", *args, **kwargs):
    self.cycled_constraints = cycle
    self.cycled_variables = [var for cn in cycle for var in cn.selected_method.outputs if cn.selected_method is not None]
    message = "%s, cns: %s, vars: %s" %(message, self.cycled_constraints, self.cycled_variables)
    super(CycleException, self).__init__(message, *args, **kwargs)

