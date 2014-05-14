
class Constraint:
  def __init__(self, check_function, strength, variables, methods):
    self.check_function = check_function
    self.strength = strength
    self.variables = variables
    self.methods = methods

    self.selected_method = None
    self.mark = None

  def is_enforced(self):
    return not self.selected_method is None

