
class ConstraintSystem:

  def __init__(self):
    self.constraints = []
    self.variables = []

  def create_variable(self, name, initialValue):
    variable = Variable(name, initialValue)
    self.variables.append(variable)

  def add_constraint(self, constraint):
    for variable in constraint.variables:
      variable.add_constraint(constraint)
    exec_roots = update_method_graph(constraint)
    exec_from_roots(exec_roots)

  def remove_constraint(self, constraint): 
    pass

  def update_method_graph(self, constraint): 
    pass

  def exec_from_roots(self, exec_roots):
    pass
