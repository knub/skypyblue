from skypyblue.models import Strength

class Mvine:
  def __init__(self, marker):
    self.marker = marker

  @property
  def mark(self):
    return self.marker.mark

  def build(self, cn, redetermined_vars):
    self.marker.new_mark()
    return self.enforce_cn(cn, cn.strength, [], redetermined_vars)

  def grow(self, root_strength, mvine_stack, redetermined_vars):
    if not mvine_stack: return True
    cn = mvine_stack.pop()
    if cn.mark == self.mark:
      ok = self.grow(root_strength, mvine_stack, redetermined_vars)
    elif Strength.weaker(cn.strength, root_strength):
      ok = self.revoke_cn(cn, root_strength, mvine_stack, redetermined_vars)
    else:
      ok = self.enforce_cn(cn, root_strength, mvine_stack, redetermined_vars)
    if not ok: mvine_stack.append(cn)
    return ok

  def revoke_cn(self, cn, root_strength, mvine_stack, redetermined_vars):
    cn.mark = self.mark
    ok = self.grow(root_strength, mvine_stack, redetermined_vars)
    if ok:
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

  def enforce_cn(self, cn, root_strength, mvine_stack, redetermined_vars):
    cn.mark = self.mark
    for mt in cn.methods:
      if self.possible_method(mt, cn, root_strength):
        next_cns = self.all_constraints_that_determine_a_var_in(mt.outputs)
        for new_cn in next_cns:
          mvine_stack.append(new_cn)
        for var in mt.outputs:
          var.mark = self.mark
        ok = self.grow(root_strength, mvine_stack, redetermined_vars)
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
          for new_cn in next_cns: mvine_stack.pop()
    cn.mark = None
    return False

  def all_constraints_that_determine_a_var_in(self, variables):
    constraints = set()
    for variable in variables:
      if variable.determined_by != None:
        constraints.add(variable.determined_by)
    return constraints

  def possible_method(self, mt, cn, root_strength):
    for var in mt.outputs:
      if var.mark == self.mark: return False
      if not Strength.weaker(var.walk_strength, root_strength):
        if cn.selected_method == None:
          return False
        if not var in cn.selected_method.outputs:
          return False
    return True
