from skypyblue.models import Variable, Method, Constraint, Strength, InternalStrength
from skypyblue.core import Mvine, Marker

import pdb;

# https://www.cs.washington.edu/research/constraints/solvers/skyblue-cycles.html
class ConstraintSystem:

  def __init__(self):
    self.marker = Marker()
    self.constraints = []
    self.variables = []
    self.forced_constraint = None
    self.check_constraints = False

    self.unenforced_constraints = set()
    self.redetermined_vars = set()
    self.exec_roots = []
    self.mark = None

  def create_variables(self, names, initialValues):
    assert len(names) == len(initialValues)
    res = []
    for i in range(len(names)):
      res.append(self.create_variable(names[i], initialValues[i]))
    return res

  # TODO: Remove these
  def create_variable(self, name, initialValue):
    variable = Variable(name, initialValue, self)
    self.variables.append(variable)
    return variable

  def change_variable_values(self, variables, values):
    if len(variables) == 1:
      values = values[0]

    m = Method([], variables,
      lambda: values)

    cn = Constraint(
      lambda x: True,
      InternalStrength.FORCED,
      variables,
      [m])

    if self.forced_constraint is not None:
      self.remove_constraint(self.forced_constraint, skip = True)

    self.forced_constraint = cn
    self.add_constraint(cn)

  def variable_changed(self, var):
    self.change_variable_values([var], [var.get_value()])

  def _check_constraints(self):
    if self.check_constraints == False:
      return
    for constraint in self.constraints:
      if not constraint.is_enforced():
        continue
      check = constraint.check_function(*[var.get_value() for var in constraint.variables])
      if not check:
        raise Exception("Constraint %s is not satisfied" % constraint)

  def add_stay_constraint(self, variable, strength):
    m = Method([], [variable], lambda: variable.get_value())
    stay_constraint = Constraint(
      lambda x: True,
      strength,
      [variable],
      [m])

    self.add_constraint(stay_constraint)
    return stay_constraint

  def add_constraint(self, constraint):
    constraint.selected_method = None
    constraint.mark = None

    for variable in constraint.variables:
      variable.add_constraint(constraint)
    self.unenforced_constraints = set([constraint])
    self.exec_roots = []
    self.update_method_graph()
    self.exec_from_roots()

    self.constraints.append(constraint)
    self._check_constraints();

  def remove_constraint(self, constraint, skip = False):
    for variable in constraint.variables:
      variable.remove_constraint(constraint)

    self.constraints.remove(constraint)
    if constraint.is_enforced():
      old_outputs = constraint.selected_method.outputs
      constraint.selected_method = None

      self.exec_roots = []
      for variable in old_outputs:
        variable.determined_by = None
        variable.walk_strength = Strength.WEAKEST
        self.exec_roots.append(variable)

      if skip:
        return

      self.propagate_walk_strength(outputs)
      self.unenforced_constraints = set()
      self.collect_unenforced(constraint.strength, True)
      self.update_method_graph()
      self.exec_from_roots()

    self._check_constraints()

  def update_method_graph(self):
    while self.unenforced_constraints:
      constraint = self.remove_strongest_constraint()
      self.redetermined_vars.clear()
      if not Mvine(self.marker).build(constraint, self.redetermined_vars):
        return
      self.propagate_walk_strength(self.redetermined_vars.union([constraint]))
      self.collect_unenforced(constraint.strength, False)
      self.exec_roots.append(constraint)
      for var in self.redetermined_vars:
        if var.determined_by is None:
          self.exec_roots.append(var)

  def remove_strongest_constraint(self):
    cn = sorted(self.unenforced_constraints, key = lambda cn: cn.strength, reverse = True)[0]
    self.unenforced_constraints.remove(cn)
    return cn

  # not used yet
  # def weakest_constraint(self, constraints):
  #   return sorted(constraints, key = lambda cn: cn.strength)[0]

  def propagate_walk_strength(self, roots):
    self._new_mark()

    for cn in self.pplan_add(roots):
      for var in cn.selected_method.inputs:
        if var.determined_by is not None and var.determined_by.mark == self.mark:
          var.walk_strength = Strength.WEAKEST
      self.compute_walkabout_strengths(cn)
      cn.mark = None

  def compute_walkabout_strengths(self, cn):
    outs = cn.selected_method.outputs
    for out_var in outs:
      max_strengths = [self.max_out(mt, outs) for mt in cn.methods if out_var not in mt.outputs]
      max_strengths.append(cn.strength)
      out_var.walk_strength = min(max_strengths)



  def max_out(self, mt, current_outputs):
    return max([var.walk_strength for var in mt.outputs if var not in current_outputs])

  def collect_unenforced(self, collection_strength, collect_equal_strength):
    self._new_mark()
    for var in self.redetermined_vars:
      stack = [var]
      while stack:
        cur_var = stack.pop()
        for cn in cur_var.constraints:
          if cn == cur_var.determined_by or cn.mark == self.mark:
            continue
          cn.mark = self.mark
          if cn.is_enforced():
            stack.extend(cn.selected_method.outputs)
          elif Strength.weaker(cn.strength, collection_strength) or \
                (collect_equal_strength and (cn.strength == collection_strength)):
            self.unenforced_constraints.add(cn)

  def any_immediate_upstream_marked(self, cn):
    for var in cn.selected_method.inputs:
      if var.determined_by is not None and var.determined_by.mark == self.mark:
        return True
    return False

  def exec_pplan_create(self):
    cn_pplan = []
    var_pplan = []
    for cn_or_var in self.exec_roots:
      if isinstance(cn_or_var, Constraint):
        cn = cn_or_var
        cn.add_to_pplan(cn_pplan, self.mark)
      elif isinstance(cn_or_var, Variable):
        var = cn_or_var
        if var.determined_by is None and not var.valid:
          var.add_to_pplan(var_pplan, self.mark)
          var.valid = True

    return cn_pplan + var_pplan

  def exec_from_roots(self):
    self._new_mark()

    for cn in reversed(self.exec_pplan_create()):
      if cn.mark == self.mark:
        if self.any_immediate_upstream_marked(cn):
          self.exec_from_cycle(cn)
        else:
          cn.mark = None
          self.execute_propagate_valid(cn)

  def execute_propagate_valid(self, cn):
    inputs_valid = not cn.selected_method.has_invalid_vars()

    if inputs_valid:
      cn.selected_method.execute()

    for var in cn.selected_method.outputs:
      var.valid = inputs_valid

  def exec_from_cycle(self, cn):
    if cn.mark == self.mark:
      cn.mark = None
      for var in cn.selected_method.outputs:
        var.valid = False
        for consuming_cn in var.constraints:
          if consuming_cn != cn and consuming_cn.is_enforced:
            self.exec_from_cycle(consuming_cn)



  def pplan_add(self, objs):
    pplan = []
    if not isinstance(objs, set):
      raise Exception("accepting only set of objs!")
    for el in objs:
      el.add_to_pplan(pplan, self.mark)
    return pplan

  def _new_mark(self):
    self.marker.new_mark()
    self.mark = self.marker.mark


  # def extract_plan(self, root_cns):
  #   good_cns = []
  #   bad_cns = []
  #   self._new_mark()
  #   pplan = self.pplan_add([], root_cns)

  #   while pplan:
  #     cn = pplan.pop()
  #     if cn.mark != self.mark:
  #       pass
  #     elif self.any_immediate_upstream_marked(cn):
  #       bad_cns.append(cn)
  #     else:
  #       cn.mark = None
  #       good_cns.append(cn)
  #   return self.create_valid_plan(root_cns, good_cns, bad_cns)

  # def create_valid_plan(self, root_cns, good_cns, bad_cns):
  #   plan = Plan(root_cns, good_cns, bad_cns)
  #   for cns in [root_cns, good_cns, bad_cns]:
  #     for cn in cns:
  #       cn.valid_plans.append(plan)
  #   return plan

  # def invalidate_plans_on_setting_method(self, cn, new_mt):
  #   self.invalidate_constraint_plans(cl.valid_plans)
  #   if new_mt != None:
  #     for var in new_mt.inputs:
  #       if var.determined_by != None:
  #         self.invalidate_constraint_plans(var.determined_by)

  # def invalidate_constraint_plans(self, invalid_cn):
  #   for plan in invalid_cn.valid_plans:
  #     plan.valid = False
  #     for cns in [plan.good_cns, plan.bad_cns, plan.root_cns]:
  #       for cn in cns:
  #         if cn != invalid_cn:
  #           cn.valid_plans.remove(plan)
  #   invalid_cn.valid_plans.clear()

  # def execute_plan(self, plan):
  #   if plan.valid:
  #     for cn in plan.good_cns:
  #       self.execute_propagate_valid(cn)
  #   else:
  #     raise ValueError("trying to execute invalid plan")



