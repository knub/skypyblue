from models.variable import Variable
from models.strengths import Strength

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
    exec_roots = self.update_method_graph([constraint])
    self.exec_from_roots(exec_roots)

  def remove_constraint(self, constraint):
    for variable in constraint.variables:
      variable.remove_constraint(constraint)
    
    if constraint.is_enforced():
      old_outputs = constraint.selected_method.outputs
      constraint.selected_method = None

      exec_roots = []

      for variable in old_outputs:
        var.determined_by = None
        var.walk_strength = Strength.WEAKEST
        exec_roots.append(variable)

      propagate_walk_strength(old_outputs)
      unenforcedConstraints = collect_unenforced(old_outputs,constraint.strength,true)

      exec_roots = update_method_graph(unenforcedConstraints,exec_roots)
      exec_from_roots(exec_roots)
      

  def update_method_graph(self, unenforcedConstraints, exec_roots=[]): 
    pass

  def exec_from_roots(self, exec_roots):
    pass

  def propagate_walk_strength(self, variables):
    pass

  def collect_unenforced(self, old_outputs, strength, booleanValue):
    pass

