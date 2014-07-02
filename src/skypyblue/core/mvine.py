from skypyblue.models import Strength

class Mvine:
  def __init__(self, marker):
    self.marker = marker
    self.mark = marker.mark
    self.stack = []
    self.root_strength = Strength.WEAKEST
    self.redetermined_vars = set()
    self.enforced, self.revoked = [], []

  def build(self, cn, redetermined_vars):
    self.marker.new_mark()
    self.mark = self.marker.mark
    self.stack = [cn]
    self.root_strength = cn.strength
    self.redetermined_vars = redetermined_vars
    if not self.determine_enforced_and_revoked():
      return False

    for cn in self.revoked:
      self.reset_outputs(cn.selected_method)
      cn.selected_method = None

    for cn, mt in self.enforced:
      if cn.selected_method is not None:
        self.reset_outputs(cn.selected_method)
      cn.selected_method = mt
      mt.mark = None
      for var in mt.outputs:
        var.determined_by = cn
        self.redetermined_vars.add(var)

    return True

  def add_conflicting_cns_to_stack(self, mt):
    # mark outputs
    # add cns, which are not marked and determine outputs of the current method
    for var in mt.outputs:
      var.mark = self.mark
      if var.determined_by is not None and var.determined_by.mark != self.mark:
        # possible dublicates?
        self.stack.append(var.determined_by)

  def backtrack(self):
    self.revoked.pop()
    cn, mt = self.enforced.pop()
    # unmark the outputs
    for var in mt.outputs: var.mark = None
    cn.mark = None
    # append last enforced cn back to the stack
    self.stack.append(cn)

  def determine_enforced_and_revoked(self):
    self.enforced, self.revoked = [], []
    while True:
      if not self.stack: break
      cn = self.stack.pop()
      if cn.mark == self.mark: continue
      cn.mark = self.mark

      if Strength.weaker(cn.strength, self.root_strength):
        self.revoked.append(cn)
      else:
        mt = self.next_possible_method(cn)
        if mt is None:
          # no method found, backtrack
          if not self.enforced or not self.revoked:
            # no backtrack possible, so we cannot enforce
            # the start constraint
            return False
          self.backtrack()
        else:
          self.enforced.append((cn, mt))
          self.add_conflicting_cns_to_stack(mt)
    return True


  def reset_outputs(self, mt):
    for var in mt.outputs:
      if var.mark != self.mark:
        var.determined_by = None
        var.walk_strength = Strength.WEAKEST
        self.redetermined_vars.add(var)

  def next_possible_method(self, cn):
    for mt in cn.methods:
      if mt.mark != self.mark and self.is_possible_method(mt, cn):
        mt.mark = self.mark
        return mt
    return None

  def is_possible_method(self, mt, cn):
    for var in mt.outputs:
      # not possible if:
      # outvar_is_marked or
      # (is_determined_by_other_stronger_cn and
      # (cn_is_not_enforced or outvar_is_output_of_selected_method)) < not already determined by cn's current method
      if var.mark == self.mark or \
      (var.walk_strength >= self.root_strength and \
      (not cn.is_enforced() or \
        var not in cn.selected_method.outputs)):
        return False
    return True
