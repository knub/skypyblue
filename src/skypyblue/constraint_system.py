class ConstraintSystem:

  def __init__(self):
    self.constraints = []
    self.variables = []

  def create_variable(self, name, initialValue):
    variable = Variable(name, initialValue)
    self.variables.append(variable)
    return variable

  def add_constraint(self, constraint):
    constraint.selected_method = None
    constraint.mark = None

    for variable in constraint.variables:
      variable.add_constraint(constraint)
    exec_roots = update_method_graph(constraint)
    exec_from_roots(exec_roots)

  def remove_constraint(self, constraint):
    for variable in constraint.variables:
      variable.remove_constraint(constraint)
    
    if constraint.is_enforced():
      old_outputs = constraint.selected_method.outputs
      constraint.selected_method = None

      

  def update_method_graph(self, constraint): 
    pass

  def exec_from_roots(self, exec_roots):
    pass
