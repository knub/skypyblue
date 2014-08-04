from skypyblue.models import *
from skypyblue.core import Mvine, Marker, CycleException, logger

import pdb


def fail_on_cylce(func):
  def wrapper(self, *args, **kwargs):
    res = func(self, *args, **kwargs)
    if self.plan.bad_constraints:
      raise CycleException(self.plan.bad_constraints, "Cycle was detected")
    return res
  return wrapper

# https://www.cs.washington.edu/research/constraints/solvers/skyblue-cycles.html
class ConstraintSystem(object):

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
    self.plan = None

    self._cycle = None

  def create_variables(self, names, initialValues):
    assert len(names) == len(initialValues)
    res = []
    for i in range(len(names)):
      res.append(Variable(names[i], initialValues[i], self))
    return res

  def change_variable_values(self, variables, values):
    if len(variables) == 1:
      values = values[0]

    m = Method([], variables,
      lambda: values)

    cn = Constraint(
      lambda x: True,
      InternalStrength.FORCED,
      variables,
      [m], "set")

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
      [m], "stay")

    self.add_constraint(stay_constraint)
    return stay_constraint

  @fail_on_cylce
  def add_constraint(self, constraint):
    constraint.selected_method = None
    constraint.mark = None

    for variable in constraint.variables:
      variable.add_constraint(constraint)
    self.unenforced_constraints = set([constraint])
    self.exec_roots = []

    self.update_method_graph()
    self.extract_plan()

    self.execute_plan()

    self.constraints.append(constraint)
    self._check_constraints()

  @fail_on_cylce
  def remove_constraint(self, constraint, skip = False):
    for variable in constraint.variables:
      variable.remove_constraint(constraint)

    self.constraints.remove(constraint)
    if constraint.is_enforced():
      old_outputs = set(constraint.selected_method.outputs)
      constraint.selected_method = None

      self.exec_roots = []
      for variable in old_outputs:
        variable.determined_by = None
        variable.walk_strength = Strength.WEAKEST
        for var_constraint in variable.constraints:
            if var_constraint.is_enforced():
              self.exec_roots.append(var_constraint)

      if skip:
        return

      self.propagate_walk_strength(old_outputs)
      self.unenforced_constraints = set()
      self.collect_unenforced(constraint.strength, True)
      self.update_method_graph()

      self.extract_plan()
      self.execute_plan()

      # self.exec_from_roots()

    self._check_constraints()

  def update_method_graph(self):
    while self.unenforced_constraints:
      constraint = self.remove_strongest_constraint()
      self.redetermined_vars.clear()
      if not Mvine(self.marker).build(constraint, self.redetermined_vars):
        continue
      self.propagate_walk_strength(self.redetermined_vars.union([constraint]))
      self.collect_unenforced(constraint.strength, False)
      self.exec_roots.append(constraint)
      self.exec_roots.extend([var_constraint \
        for var in self.redetermined_vars \
          for var_constraint in var.constraints \
            if var.determined_by is None and \
              var_constraint.is_enforced()])
    # logger.DEBUG("exec_roots: %s" %self.exec_roots)

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

  def immediate_marked_upstream(self, cn):
    return [var.determined_by for var in cn.selected_method.inputs if var.determined_by is not None and var.determined_by.mark == self.mark]

  # def exec_pplan_create(self):
  #   cn_pplan = []
  #   var_pplan = []
  #   for cn_or_var in self.exec_roots:
  #     if isinstance(cn_or_var, Constraint):
  #       cn = cn_or_var
  #       cn.add_to_pplan(cn_pplan, self.mark)
  #     elif isinstance(cn_or_var, Variable):
  #       var = cn_or_var
  #       if var.determined_by is None and not var.valid:
  #         var.add_to_pplan(var_pplan, self.mark)
  #         var.valid = True
  #   pplan = cn_pplan + var_pplan
  #   # logger.DEBUG("pplan:\t%s" %", ".join([str(cn) for cn in reversed(pplan)]))
  #   # logger.DEBUG("marks:\t%s" %", ".join([str(cn.mark) for cn in reversed(pplan)]))
  #   return pplan

  # def exec_from_roots(self):
  #   self._new_mark()

  #   for cn in reversed(self.exec_pplan_create()):
  #     if cn.mark == self.mark:
  #       if self.any_immediate_upstream_marked(cn):
  #         self.exec_from_cycle(cn)
  #       else:
  #         cn.mark = None
  #         self.execute_propagate_valid(cn)

  def execute_propagate_valid(self, cn):
    inputs_valid = not cn.selected_method.has_invalid_vars()

    if inputs_valid:
      cn.selected_method.execute()

    for var in cn.selected_method.outputs:
      var.valid = inputs_valid

  # def exec_from_cycle(self, cn):
  #   if self._cycle is None: self._cycle = set()
  #   self._cycle.add(cn)

  #   if cn.mark == self.mark:
  #     cn.mark = None
  #     for var in cn.selected_method.outputs:
  #       var.valid = False
  #       for consuming_cn in var.constraints:
  #         if consuming_cn != cn and consuming_cn.is_enforced:
  #           self.exec_from_cycle(consuming_cn)



  def pplan_add(self, objs):
    pplan = []
    if not isinstance(objs, set) and not isinstance(objs, list):
      raise Exception("accepting only set of objs! Got %s of type %s" %(objs, type(objs)))
    for el in objs:
      el.add_to_pplan(pplan, self.mark)
    return pplan


  def _new_mark(self):
    self.marker.new_mark()
    self.mark = self.marker.mark


  # create-valid-plan in now Plan(....)
  # invalidate-constraint-plans is now constraint.invalidate_plans()
  # invalidate_plans_on_setting_method moved to constraint
  def extract_plan(self):
    if self.plan is None or not self.plan.valid:
      good_constraints = []
      bad_constraints = []
      self._new_mark()

      for cn in reversed(self.pplan_add(self.exec_roots)):
        if cn.mark != self.mark:
          continue
        elif self.any_immediate_upstream_marked(cn):
          bad_constraints.append(cn)
        else:
          cn.mark = None
          good_constraints.append(cn)
      self.plan = Plan(self.exec_roots, good_constraints, bad_constraints, True)


  def execute_plan(self):
    if self.plan.valid:
      for cn in self.plan.good_constraints:
        self.execute_propagate_valid(cn)
    else:
      raise ValueError("trying to execute invalid plan")



