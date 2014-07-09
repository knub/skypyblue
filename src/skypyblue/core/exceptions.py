

class CycleException(Exception):
  """Constraint system raises this exception, if a cycle was detected"""
  def __init__(self, bad_constraints, message = "", *args, **kwargs):
    self.cycled_constraints = bad_constraints
    self.cycled_variables = [var for cn in bad_constraints for var in cn.selected_method.outputs if cn.selected_method is not None]
    for var in self.cycled_variables:
      var.valid = False
    message = "%s, cns: %s, vars: %s" %(message, self.cycled_constraints, self.cycled_variables)
    super(CycleException, self).__init__(message, *args, **kwargs)

