from skypyblue.models import Strength

class Mvine:
  def __init__(self, marker):
    self.marker = marker
    self.stack = []
    self.root_strength = Strength.WEAKEST
    self.redetermined_vars = set()

  @property
  def mark(self):
    return self.marker.mark

  def build(self, cn, redetermined_vars):
    self.marker.new_mark()
    self.stack = []
    self.root_strength = cn.strength
    self.redetermined_vars = redetermined_vars
    return self.enforce_cn_iterative(cn)

  def grow(self):
    if not self.stack: return True
    cn = self.stack.pop()
    if cn.mark == self.mark:
      ok = self.grow()
    elif Strength.weaker(cn.strength, self.root_strength):
      ok = self.revoke_cn(cn)
    else:
      ok = self.enforce_cn(cn)
    if not ok: self.stack.append(cn)
    return ok

  def revoke_cn(self, cn):
    cn.mark = self.mark
    if self.grow():
      for var in cn.selected_method.outputs:
        if var.mark != self.mark:
          var.determined_by = None
          var.walk_strength = Strength.WEAKEST
          self.redetermined_vars.add(var)
      cn.selected_method = None
      return True
    else:
      cn.mark = None
      return False

  def enforce_cn(self, cn):
    cn.mark = self.mark
    for mt in cn.methods:
      if self.is_possible_method(mt, cn):
        next_cns = self.all_constraints_that_determine_a_var_in(mt.outputs)
        for new_cn in next_cns:
          self.stack.append(new_cn)
        for var in mt.outputs:
          var.mark = self.mark
        if self.grow():
          if cn.selected_method is not None:
            for var in cn.selected_method.outputs:
              if var.mark != self.mark:
                var.determined_by = None
                var.walk_strength = Strength.WEAKEST
                self.redetermined_vars.add(var)
          cn.selected_method = mt
          for var in mt.outputs:
            var.determined_by = cn
            self.redetermined_vars.add(var)
          return True
        else:
          for var in mt.outputs: var.mark = None
          for new_cn in next_cns: self.stack.pop()
    cn.mark = None
    return False


  def enforce_cn_iterative(self, constraint):
    stack = [constraint]
    enforced = {}
    revoked = {}
    enforced_step, revoked_step = 0, 0
    while True:
      if not stack: break
      cn = stack.pop()
      if cn.mark == self.mark: continue
      cn.mark = self.mark

      if Strength.weaker(cn.strength, self.root_strength):
        # revoke part
        revoked_step += 1
        revoked[revoked_step] = cn
      else:
        # enforce part
        mt = self.next_possible_method(cn)
        if mt is None:
          # no method found, backtrack
          if not enforced or not revoked:
            # no backtrack possible, so we cannot enforce the start constraint
            return False
          revoked.pop(revoked_step)
          revoked_step -= 1
          cn, mt = enforced.pop(enforced_step)
          enforced_step -= 1
          # unmark the outputs
          for var in mt.outputs: var.mark = None
          cn.mark = None
          # append last enforced cn back to the stack
          stack.append(cn)
        else:
          enforced_step += 1
          enforced[enforced_step] = (cn, mt)
          # mark outputs
          # add cns, which are not marked and determine outputs of the current method
          for var in mt.outputs:
            var.mark = self.mark
            if var.determined_by is not None and var.determined_by.mark != self.mark:
              # possible dublicates?
              stack.append(var.determined_by)


    def reset_outputs(mt):
      for var in mt.outputs:
        if var.mark != self.mark:
          var.determined_by = None
          var.walk_strength = Strength.WEAKEST
          self.redetermined_vars.add(var)

    for cn in revoked.values():
      reset_outputs(cn.selected_method)
      cn.selected_method = None

    for cn, mt in enforced.values():
      if cn.selected_method is not None:
        reset_outputs(cn.selected_method)
      cn.selected_method = mt
      mt.mark = None
      for var in mt.outputs:
        var.determined_by = cn
        self.redetermined_vars.add(var)

    return True

  def next_possible_method(self, cn):
    for mt in cn.methods:
      if mt.mark != self.mark and self.is_possible_method(mt, cn):
        mt.mark = self.mark
        return mt
    return None

  def all_constraints_that_determine_a_var_in(self, variables):
    return set([var.determined_by for var in variables if var.determined_by is not None])

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
