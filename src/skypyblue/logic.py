from models.strengths import Strength

weaker = Strength.weaker


def add_constraint(cn):
  unenforced_cns = []
  cn.selected_method = None
  cn.mark = None
  for var in cn.variables:
    var.constraints.append(cn)
  unenforced_cns.append(cn)
  exec_roots = update_method_graph(unenforced_cns)
  exec_from_roots(exec_roots)

def remove_constraint(cn):
  for var in cn.variables:
    var.constraints.remove(cn)
  if not cn.enforced(): return 
  unenforced_cns = []
  exec_roots = []
  cn_old_outputs = cn.selected_method.outputs
  cn.selected_method = None
  for var in cn_old_outputs:
    var.determined_by = None
    var.walk_strength = Strength.WEAKEST
  exec_roots = cn_old_outputs
  propagate_walk_strength(cn_old_outputs)
  unenforced_cns = collect_unenforced(cn_old_outputs, cn.strength, True)
  exec_roots = update_method_graph(unenforced_cns, exec_roots)
  exec_from_roots(exec_roots)

def update_method_graph(unenforced_cns, exec_roots):
  while not unenforced_cns:
    cn = strongest_constraint(unenforced_cns)
    unenforced_cns.remove(cn)
    redetermined_vars, ok = build_mvine(cn, redetermined_vars)
    if not ok: return
    propagate_walk_strength([cn] + [redetermined_vars])
    unenforced_cns = collect_unenforced(redetermined_vars, cn.strength, false)
    exec_roots.append(cn)
    for var in redetermined_vars:
      if var.determined_by is None:
        exec_roots.append(var)
    return exec_roots

def build_mvine(cn, redetermined_vars):
  mvine_stack = []
  done_mark = new_mark()

  return mvine_enforce_cn(cn, cn.strength, done_mark, mvine_stack, redetermined_vars)

def mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars):
  if not mvine_stack: return True
  cn = mvine_stack.pop()
  if cn.mark == done_mark:
    ok = mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars)
  elif weaker(cn.strength, root_strength):
    ok = mvine_revoke_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars)
  else:
    ok = mvine_enforce_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars)
  if not ok: mvine_stack.append(cn)
  return ok

def mvine_revoke_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars):
  cn.mark = done_mark
  if mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars):
    for var in cn.selected_method.outputs:
      if var.mark != done_mark:
        var.determined_by = None
        var.walk_strength = Strength.WEAKEST
        redetermined_vars.append(var)
    cn.selected_method = None
    return True
  else:
    cn.mark = None
    return False

def mvine_enforce_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars):
  cn.mark = done_mark
  for mt in cn.methods:
    if possible_method(mt, cn, root_strength, done_mark):
      next_cns = all_constraints_that_determine_a_var_in(mt.outputs)
      for new_cn in next_cns: 
        mvine_stack.append(new_cn)
      for var in mt.outputs:
        var.mark = done_mark
      ok = mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars)
      if ok:
        if not cn.selected_method is None:
          for var in cn.selected_method.outputs:
            if var.mark != done_mark:
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

def possible_method(mt, cn, root_strength, done_mark):
  for var in mt.outputs:
    if var.mark == done_mark: return False
    if not weaker(var.walk_strength, root_strength):
      if cn.selected_method == None: 
        return False
      if not var in cn.selected_method.outputs: 
        return False
  return True

def propagate_walk_strength(roots):
  prop_mark = new_mark()
  walk_pplan = pplan_add(walk_pplan, roots, prop_mark)

  while walk_pplan:
    cn = walk_pplan.pop()
    if any_immediate_upstream_marked(cn, prop_mark):
      for var  in cn.selected_method.inputs:
        if var.determined_by != None:
          if var.determined_by.mark == prop_mark:
            var.walk_strength = Strength.WEAKEST
    compute_walkabout_strengths(cn)
    cn.mark = None

def any_immediate_upstream_marked(cn, mark):
  for var in cn.selected_method.inputs:
      if var.determined_by != None and var.determined_by.mark == mark:
        return True
  return False

def compute_walkabout_strengths(cn):
  current_outputs = cn.selected_method.outputs
  for out_var in current_outputs:
    min_strength = cn.strength
    for mt in cn.methods:
      if not out_var in mt.outputs:
        max_strength = max_out(mt, current_outputs)
        if weaker(max_strength, min_strength):
          min_strength = max_strength
    out_var.walk_strength = min_strength

def collect_unenforced(unenforced_cns, vars, collection_strength, collect_equal_strength):
  done_mark = new_mark()
  for var in vars:
    unenforced_cns.extend(collect_unenforced_mark(unenforced_cns, var, collection_strength, collect_equal_strength, done_mark))
  return unenforced_cns

def collect_unenforced_mark(unenforced_cns, var, collection_strength, collect_equal_strength, done_mark):
  for cn in var.constraints:
    if cn != var.determined_by and cn.mark != done_mark:
      cn.mark = done_mark
      if cn.enforced():
        for out_var in cn.selected_method.outputs:
          collect_unenforced_mark(unenforced_cns, out_var, collection_strength, collect_equal_strength, done_mark)
      elif weaker(cn.strength, collection_strength) or \
            (collect_equal_strength and (cn.strength == collection_strength)):
        unenforced_cns.append(cn)
  return unenforced_cns

def exec_from_root(exec_roots):
  prop_mark = new_mark()
  exec_pplan = []
  for cn in exec_roots:
    exec_pplan.extend(pplan_add(exec_pplan, cn, prop_mark))

  for var in exec_roots:
    if var.determined_by == None and not var.valid:
      exec_pplan.extend(var, prop_mark)
      var.valid = True

  while exec_pplan:
    cn = exec_pplan.pop()
    if cn.mark != prop_mark:
      # this cn has already been processed: do nothing
      # WTF?
      pass
    elif any_immediate_upstream_marked(cn, prop_mark):
      exec_from_cycle(cn, prop_mark)
    else:
      cn.mark = None
      execute_propagate_valid(cn)

def execute_propagate_valid(cm):
  inputs_valid = True
  for var in cn.selected_method.inputs:
    if not var.valid:
      inputs_valid = False
  if inputs_valid:
    cn.selected_method.execute()
  for var in cn.selected_method.outputs:
    var.valid = inputs_valid

def exec_from_cycle(cn, prop_mark):
  if cn.mark == prop_mark:
    cn.mark = None
    for var in cn.selected_method.outputs:
      var.valid = False
      for consuming_cn in var.constraints:
        if consuming_cn != cn and consuming_cn.enforced():
          exec_from_cycle(consuming_cn, prop_mark)

def pplan_add(pplan, obj, done_mark):
  if isinstance(obj, Constraint):
    if obj.enforced() and obj.mark != done_mark:
      obj.mark = done_mark
      for var in obj.selected_method.outputs:
        pplan.extend(pplan_add(pplan, var, done_mark))
      pplan.append(obj)
  elif isinstance(obj, Variable):
    for cn in obj.constraints:
      if cn != var.determined_by:
        pplan.extend(pplan, cn, done_mark)
  elif isinstance(obj, list):
    for elt in obj:
      pplan.extend(pplan_add(pplan, elt, done_mark))

  return pplan

def extract_plan(root_cns):
  good_cns = []
  bad_cns = []
  prop_mark = new_mark()
  pplan = pplan_add([], root_cns, prop_mark)

  while pplan:
    cn = pplan.pop()
    if cn.mark != prop_mark:
      pass
    elif any_immediate_upstream_marked(cn, prop_mark):
      bad_cns.append(cn)
    else:
      cn.mark = None
      good_cns.append(cn)
  return create_valid_plan(root_cns, good_cns, bad_cns)

def create_valid_plan(root_cns, good_cns, bad_cns):
  plan = Plan(root_cns, good_cns, bad_cns)
  for cns in [root_cns, good_cns, bad_cns]:
    for cn in cns:
      cn.valid_plans.append(plan)
  return plan

def invalidate_plans_on_setting_method(cn, new_mt):
  invalidate_constraint_plans(cl.valid_plans)
  if new_mt != None:
    for var in new_mt.inputs:
      if var.determined_by != None:
        invalidate_constraint_plans(var.determined_by)

def invalidate_constraint_plans(invalid_cn):
  for plan in invalid_cn.valid_plans:
    plan.valid = False
    for cns in [plan.good_cns, plan.bad_cns, plan.root_cns]:
      for cn in cns:
        if cn != invalid_cn: 
          cn.valid_plans.remove(plan)
  invalid_cn.valid_plans.clear()

def execute_plan(plan):
  if plan.valid:
    for cn in plan.good_cns:
      execute_propagate_valid(cn)
  else:
    raise ValueError("trying to execute invalid plan")


c = 0
def new_mark():
  global c
  c += 1
  return c


def max_out(mt, current_outputs):
  max_strength = Strength.WEAKEST
  for var in mt.outputs:
    if not var in current_outputs and \
      weaker(max_strength, var.walk_strength):
      max_strength = var.walk_strength
  return max_strength

