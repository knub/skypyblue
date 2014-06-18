from skypyblue.models import Strength

class Mvine:
  def __init__(self, marker):
    self.marker = marker
    self.stack = []
    self.root_strength = Strength.WEAKEST

  @property
  def mark(self):
    return self.marker.mark

  def build(self, cn, redetermined_vars):
    self.marker.new_mark()
    self.stack = []
    self.root_strength = cn.strength
    return self.enforce_cn(cn, redetermined_vars)

  def grow(self, redetermined_vars):
    if not self.stack: return True
    cn = self.stack.pop()
    if cn.mark == self.mark:
      ok = self.grow(redetermined_vars)
    elif Strength.weaker(cn.strength, self.root_strength):
      ok = self.revoke_cn(cn, redetermined_vars)
    else:
      ok = self.enforce_cn(cn, redetermined_vars)
    if not ok: self.stack.append(cn)
    return ok

  def revoke_cn(self, cn, redetermined_vars):
    cn.mark = self.mark
    if self.grow(redetermined_vars):
      for var in cn.selected_method.outputs:
        if var.mark != self.mark:
          var.determined_by = None
          var.walk_strength = Strength.WEAKEST
          redetermined_vars.append(var)
      cn.selected_method = None
      return True
    else:
      cn.mark = None
      return False

  def enforce_cn(self, cn, redetermined_vars):
    cn.mark = self.mark
    for mt in cn.methods:
      if self.is_possible_method(mt, cn):
        next_cns = self.all_constraints_that_determine_a_var_in(mt.outputs)
        for new_cn in next_cns:
          self.stack.append(new_cn)
        for var in mt.outputs:
          var.mark = self.mark
        ok = self.grow(redetermined_vars)
        if ok:
          if not cn.selected_method is None:
            for var in cn.selected_method.outputs:
              if var.mark != self.mark:
                var.determined_by = None
                var.walk_strength = Strength.WEAKEST
                redetermined_vars.append(var)
          cn.selected_method = mt
          for var in mt.outputs:
            var.determined_by = cn
            redetermined_vars.append(var)
          return True
        else:
          for var in mt.outputs: var.mark = None
          for new_cn in next_cns: self.stack.pop()
    cn.mark = None
    return False

  def all_constraints_that_determine_a_var_in(self, variables):
    return set([var.determined_by for var in variables if var.determined_by is not None])

  def is_possible_method(self, mt, cn):
    for var in mt.outputs:
      # boolean expression: A or (B and (C or D))
      if var.mark == self.mark or \
      (var.walk_strength >= self.root_strength and \
      (cn.selected_method == None or \
        var not in cn.selected_method.outputs)):
        return False
    return True
