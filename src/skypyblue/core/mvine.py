from skypyblue.models import Strength

class Mvine(object):
  def __init__(self, marker):
    self.marker = marker
    self.mark = marker.mark
    self.stack = []
    self.root_strength = Strength.WEAKEST
    self.redetermined_variables = set()
    self.enforced, self.revoked = [], []

  def build(self, constraint, redetermined_variables):
    self.marker.new_mark()
    self.mark = self.marker.mark
    self.stack = [constraint]
    self.root_strength = constraint.strength
    self.redetermined_variables = redetermined_variables
    if not self.determine_enforced_and_revoked():
      return False

    for constraint in self.revoked:
      self.reset_outputs(constraint.selected_method)
      constraint.selected_method = None

    for constraint, method in self.enforced:
      if constraint.selected_method is not None:
        self.reset_outputs(constraint.selected_method)
      constraint.selected_method = method
      method.mark = None
      for variable in method.outputs:
        variable.determined_by = constraint
        self.redetermined_variables.add(variable)

    return True

  def add_conflicting_cns_to_stack(self, method):
    # mark outputs
    # add cns, which are not marked and determine outputs of the current method
    for variable in method.outputs:
      variable.mark = self.mark
      if variable.determined_by is not None and variable.determined_by.mark != self.mark:
        # possible dublicates?
        self.stack.append(variable.determined_by)

  def backtrack(self):
    self.revoked.pop()
    constraint, method = self.enforced.pop()
    # unmark the outputs
    for variable in method.outputs: variable.mark = None
    constraint.mark = None
    # append last enforced cn back to the stack
    self.stack.append(constraint)

  def determine_enforced_and_revoked(self):
    self.enforced, self.revoked = [], []
    while True:
      if not self.stack: break
      constraint = self.stack.pop()
      if constraint.mark == self.mark: continue
      constraint.mark = self.mark

      if Strength.weaker(constraint.strength, self.root_strength):
        self.revoked.append(constraint)
      else:
        method = self.next_possible_method(constraint)
        if method is None:
          # no method found, backtrack
          if not self.enforced or not self.revoked:
            # no backtrack possible, so we cannot enforce
            # the start constraint
            return False
          self.backtrack()
        else:
          self.enforced.append((constraint, method))
          self.add_conflicting_cns_to_stack(method)
    return True


  def reset_outputs(self, method):
    for variable in method.outputs:
      if variable.mark != self.mark:
        variable.determined_by = None
        variable.walk_strength = Strength.WEAKEST
        self.redetermined_variables.add(variable)

  def next_possible_method(self, constraint):
    for method in constraint.methods:
      if method.mark != self.mark and self.is_possible_method(method, constraint):
        method.mark = self.mark
        return method
    return None

  def is_possible_method(self, method, constraint):
    for variable in method.outputs:
      # not possible if:
      # outvar_is_marked or
      # (is_determined_by_other_stronger_cn and
      # (cn_is_not_enforced or outvar_is_output_of_selected_method)) < not already determined by cn's current method
      if variable.mark == self.mark or \
      (variable.walk_strength >= self.root_strength and \
      (not constraint.is_enforced() or \
        variable not in constraint.selected_method.outputs)):
        return False
    return True
