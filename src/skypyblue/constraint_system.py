from models import Variable, Method, Constraint, Strength, InternalStrength
import pdb;

class ConstraintSystem:

  def __init__(self):
    self.c = 0
    self.constraints = []
    self.variables = []
    self.forced_constraint = None

  def create_variable(self, name, initialValue):
    variable = Variable(name, initialValue, self)
    self.variables.append(variable)
    return variable

  def change_variable_values(self, variables, values):
    if len(variables)==1:
      values = values[0]
      
    m = Method([], variables,
      lambda: values)

    cn = Constraint(
      lambda x: True,
      InternalStrength.FORCED,
      variables, 
      [m])

    if self.forced_constraint is not None:
      self.remove_constraint(self.forced_constraint)

    self.forced_constraint = cn
    self.add_constraint(cn)


  def variable_changed(self, var):
    self.change_variable_values([var], [var.value])

  def add_constraint(self, constraint):
    constraint.selected_method = None
    constraint.mark = None

    for variable in constraint.variables:
      variable.add_constraint(constraint)
    exec_roots = []
    self.update_method_graph([constraint], exec_roots)
    self.exec_from_roots(exec_roots)

  def remove_constraint(self, constraint):
    for variable in constraint.variables:
      variable.remove_constraint(constraint)
    
    if constraint.is_enforced():
      old_outputs = constraint.selected_method.outputs
      constraint.selected_method = None
      
      exec_roots = []
      for variable in old_outputs:
        variable.determined_by = None
        variable.walk_strength = Strength.WEAKEST
        exec_roots.append(variable)

      self.propagate_walk_strength(old_outputs)
      unenforcedConstraints = []
      self.collect_unenforced(unenforcedConstraints, old_outputs,constraint.strength,True)
      exec_roots = []
      self.update_method_graph(unenforcedConstraints,exec_roots)
      self.exec_from_roots(exec_roots)
      

  def update_method_graph(self, unenforced_constraints, exec_roots): 
    while unenforced_constraints:
      cn = self.strongest_constraint(unenforced_constraints)
      unenforced_constraints = list(
        filter(lambda c: c != cn, unenforced_constraints))
      redetermined_vars = []
      ok = self.build_mvine(cn, redetermined_vars)
      if not ok: return
      self.propagate_walk_strength([cn] + [redetermined_vars])
      self.collect_unenforced(unenforced_constraints, redetermined_vars, cn.strength, False)
      exec_roots.append(cn)
      for var in redetermined_vars:
        if var.determined_by is None:
          exec_roots.append(var)

  def strongest_constraint(self, constraints):
    constraints.sort(key = lambda cn: cn.strength, reverse = True)
    return constraints[0]

  def weakest_constraint(self, constraints):
    constraints.sort(key=lambda cn: cn.strength)  
    return constraints[0]

  def build_mvine(self, cn, redetermined_vars):
    mvine_stack = []
    done_mark = self.new_mark()
    return self.mvine_enforce_cn(cn, cn.strength, done_mark, mvine_stack, redetermined_vars)

  def mvine_grow(self, root_strength, done_mark, mvine_stack, redetermined_vars):
    if not mvine_stack: return True
    cn = mvine_stack.pop()
    if cn.mark == done_mark:
      ok = self.mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars)
    elif Strength.weaker(cn.strength, root_strength):
      ok = self.mvine_revoke_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars)
    else:
      ok = self.mvine_enforce_cn(cn, root_strength, done_mark, mvine_stack, redetermined_vars)
    if not ok: mvine_stack.append(cn)
    return ok

  def mvine_revoke_cn(self, cn, root_strength, done_mark, mvine_stack, redetermined_vars):
    cn.mark = done_mark
    ok = self.mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars)
    if ok:
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

  def mvine_enforce_cn(self, cn, root_strength, done_mark, mvine_stack, redetermined_vars):
    cn.mark = done_mark
    for mt in cn.methods:
      if self.possible_method(mt, cn, root_strength, done_mark):
        next_cns = self.all_constraints_that_determine_a_var_in(mt.outputs)
        for new_cn in next_cns: 
          mvine_stack.append(new_cn)
        for var in mt.outputs:
          var.mark = done_mark
        ok = self.mvine_grow(root_strength, done_mark, mvine_stack, redetermined_vars)
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

  def all_constraints_that_determine_a_var_in(self, variables):
    constraints = set()
    for variable in variables:
      if variable.determined_by != None:
        constraints.add(variable.determined_by)
    return constraints

  def possible_method(self, mt, cn, root_strength, done_mark):
    for var in mt.outputs:
      if var.mark == done_mark: return False
      if not Strength.weaker(var.walk_strength, root_strength):
        if cn.selected_method == None: 
          return False
        if not var in cn.selected_method.outputs: 
          return False
    return True

  def propagate_walk_strength(self, roots):
    prop_mark = self.new_mark()
    walk_pplan = []
    self.pplan_add(walk_pplan, roots, prop_mark)

    while walk_pplan:
      cn = walk_pplan.pop()
      if self.any_immediate_upstream_marked(cn, prop_mark):
        for var  in cn.selected_method.inputs:
          if var.determined_by != None:
            if var.determined_by.mark == prop_mark:
              var.walk_strength = Strength.WEAKEST
      self.compute_walkabout_strengths(cn)
      cn.mark = None

  def any_immediate_upstream_marked(self, cn, mark):
    for var in cn.selected_method.inputs:
        if var.determined_by != None and var.determined_by.mark == mark:
          return True
    return False

  def compute_walkabout_strengths(self, cn):
    current_outputs = cn.selected_method.outputs
    for out_var in current_outputs:
      min_strength = cn.strength
      for mt in cn.methods:
        if not out_var in mt.outputs:
          max_strength = max_out(mt, current_outputs)
          if Strength.weaker(max_strength, min_strength):
            min_strength = max_strength
      out_var.walk_strength = min_strength

  def collect_unenforced(self, unenforced_cns, vars, collection_strength, collect_equal_strength):
    done_mark = self.new_mark()
    for var in vars:
      unenforced_cns.extend(self.collect_unenforced_mark(unenforced_cns, var, collection_strength, collect_equal_strength, done_mark))
    return unenforced_cns

  def collect_unenforced_mark(self, unenforced_cns, var, collection_strength, collect_equal_strength, done_mark):
    for cn in var.constraints:
      if cn != var.determined_by and cn.mark != done_mark:
        cn.mark = done_mark
        if cn.is_enforced():
          for out_var in cn.selected_method.outputs:
            self.collect_unenforced_mark(unenforced_cns, out_var, collection_strength, collect_equal_strength, done_mark)
        elif Strength.weaker(cn.strength, collection_strength) or \
              (collect_equal_strength and (cn.strength == collection_strength)):
          unenforced_cns.append(cn)
    return unenforced_cns

  def exec_from_roots(self, exec_roots):
    prop_mark = self.new_mark()
    exec_pplan = []

    for cn in exec_roots:
      if isinstance(cn, Constraint):
        exec_pplan.extend(self.pplan_add(exec_pplan, cn, prop_mark))

    for var in exec_roots:
      if isinstance(var, Variable):
        if var.determined_by == None and not var.valid:
          exec_pplan.extend(var, prop_mark)
          var.valid = True

    while exec_pplan:
      cn = exec_pplan.pop()
      if cn.mark != prop_mark:
        # this cn has already been processed: do nothing
        # WTF?
        pass
      elif self.any_immediate_upstream_marked(cn, prop_mark):
        self.exec_from_cycle(cn, prop_mark)
      else:
        cn.mark = None
        self.execute_propagate_valid(cn)

  def execute_propagate_valid(self, cn):
    inputs_valid = True
    for var in cn.selected_method.inputs:
      if not var.valid:
        inputs_valid = False
    if inputs_valid:
      cn.selected_method.execute()
    for var in cn.selected_method.outputs:
      var.valid = inputs_valid

  def exec_from_cycle(self, cn, prop_mark):
    if cn.mark == prop_mark:
      cn.mark = None
      for var in cn.selected_method.outputs:
        var.valid = False
        for consuming_cn in var.constraints:
          if consuming_cn != cn and consuming_cn.is_enforced:
            self.exec_from_cycle(consuming_cn, prop_mark)

  def pplan_add(self, pplan, obj, done_mark):
    if isinstance(obj, Constraint):
      if obj.is_enforced() and obj.mark != done_mark:
        obj.mark = done_mark
        for var in obj.selected_method.outputs:
          pplan.extend(self.pplan_add(pplan, var, done_mark))
        pplan.append(obj)
    elif isinstance(obj, Variable):
      for cn in obj.constraints:
        if cn != obj.determined_by:
          self.pplan_add(pplan, cn, done_mark)
    elif isinstance(obj, list):
      for elt in obj:
        self.pplan_add(pplan, elt, done_mark)

    return pplan

  def extract_plan(self, root_cns):
    good_cns = []
    bad_cns = []
    prop_mark = self.new_mark()
    pplan = self.pplan_add([], root_cns, prop_mark)

    while pplan:
      cn = pplan.pop()
      if cn.mark != prop_mark:
        pass
      elif self.any_immediate_upstream_marked(cn, prop_mark):
        bad_cns.append(cn)
      else:
        cn.mark = None
        good_cns.append(cn)
    return self.create_valid_plan(root_cns, good_cns, bad_cns)

  def create_valid_plan(self, root_cns, good_cns, bad_cns):
    plan = Plan(root_cns, good_cns, bad_cns)
    for cns in [root_cns, good_cns, bad_cns]:
      for cn in cns:
        cn.valid_plans.append(plan)
    return plan

  def invalidate_plans_on_setting_method(self, cn, new_mt):
    self.invalidate_constraint_plans(cl.valid_plans)
    if new_mt != None:
      for var in new_mt.inputs:
        if var.determined_by != None:
          self.invalidate_constraint_plans(var.determined_by)

  def invalidate_constraint_plans(self, invalid_cn):
    for plan in invalid_cn.valid_plans:
      plan.valid = False
      for cns in [plan.good_cns, plan.bad_cns, plan.root_cns]:
        for cn in cns:
          if cn != invalid_cn: 
            cn.valid_plans.remove(plan)
    invalid_cn.valid_plans.clear()

  def execute_plan(self, plan):
    if plan.valid:
      for cn in plan.good_cns:
        self.execute_propagate_valid(cn)
    else:
      raise ValueError("trying to execute invalid plan")


  def new_mark(self):
    self.c+=1
    return self.c


def max_out(mt, current_outputs):
  max_strength = Strength.WEAKEST
  for var in mt.outputs:
    if not var in current_outputs and \
      Strength.weaker(max_strength, var.walk_strength):
      max_strength = var.walk_strength
  return max_strength



