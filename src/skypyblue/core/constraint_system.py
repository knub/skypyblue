from skypyblue.models import *
from skypyblue.core import Mvine, Marker, CycleException, logger


def fail_on_cycle(func):
  def wrapper(self, *args, **kwargs):
    res = func(self, *args, **kwargs)
    if self.plan.bad_constraints:
      raise CycleException(self.plan.bad_constraints, "Cycle was detected")
    return res
  return wrapper

# https://www.cs.washington.edu/research/constraints/solvers/skyblue-cycles.html

class ConstraintSystem(object):
  """This class encapsulates a set of constraints.

  Usage:
  >>> cs = ConstraintSystem()
  >>> v1 = Variable("v1", 1, cs)
  >>> v2 = Variable("v2", 2, cs)

  >>> m1 = Method([v1], [v2], lambda v1: v1)
  >>> m2 = Method([v2], [v2], lambda v2: v2)

  >>> constraint = Constraint(
  >>>   lambda v1, v2: v1 == v2,
  >>>   Strength.STRONG,
  >>>   [v1, v2], [m1, m2])
  >>> cs.add_constraint(constraint)

  >>> v1.get_value() # => 1
  >>> v2.get_value() # => 1
  """

  def __init__(self):
    self.marker = Marker()
    self.constraints = []
    self.variables = []
    self.forced_constraint = None
    self.check_constraints = False
    self.unenforced_constraints = set()
    self.redetermined_variables = set()
    self.exec_roots = []
    self.mark = None
    self.plan = None
    self._cycle = None

  def create_variables(self, names, initialValues):
    """
    Creates several variables at once.
    >>> v1, v2, v3 = constraint_system.create_variables(["v1", "v2", "v3"], [4, 5, 3])
    """
    assert len(names) == len(initialValues)
    variables = []
    for i in range(len(names)):
      variables.append(Variable(names[i], initialValues[i], self))
    return variables

  def change_variable_values(self, variables, values):
    """Allows to change several variables at once.

    >>> constraint_system.change_variable_values(
    >>>     [self.v1, self.v2],
    >>>     [10, 20]
    >>> )
    """
    assert len(variables) == len(values)

    if len(variables) == 1:
      values = values[0]

    method = Method([], variables,
      lambda: values)

    constraint = Constraint(
      lambda x: True,
      InternalStrength.FORCED,
      variables,
      [method],
      "set")

    if self.forced_constraint is not None:
      self.remove_constraint(self.forced_constraint, skip = True)
    self.forced_constraint = constraint
    self.add_constraint(constraint)

  def _variable_changed(self, variable):
    self.change_variable_values([variable], [variable.get_value()])

  def _check_constraints(self):
    if self.check_constraints == False:
      return
    for constraint in self.constraints:
      if not constraint.is_enforced():
        continue
      check = constraint.check_function(*[var.get_value() for var in constraint.variables])
      if not check:
        raise Exception("Constraint %s is not satisfied" % constraint)

  def _add_stay_constraint(self, variable, strength):
    method = Method([], [variable], lambda: variable.get_value())
    stay_constraint = Constraint(
      lambda x: True,
      strength,
      [variable],
      [method], "stay")

    self.add_constraint(stay_constraint)
    return stay_constraint

  @fail_on_cycle
  def add_constraint(self, constraint):
    constraint.selected_method = None
    constraint.mark = None

    for variable in constraint.variables:
      variable.add_constraint(constraint)
    self.unenforced_constraints = set([constraint])
    self.exec_roots = []

    self._update_method_graph()
    self._extract_plan()

    self._execute_plan()

    self.constraints.append(constraint)
    self._check_constraints()

  @fail_on_cycle
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

      self._propagate_walk_strength(old_outputs)
      self.unenforced_constraints = set()
      self._collect_unenforced(constraint.strength, True)
      self._update_method_graph()

      self._extract_plan()
      self._execute_plan()

    self._check_constraints()

  def _update_method_graph(self):
    while self.unenforced_constraints:
      constraint = self._remove_strongest_constraint()
      self.redetermined_variables.clear()
      if not Mvine(self.marker).build(constraint, self.redetermined_variables):
        continue
      self._propagate_walk_strength(self.redetermined_variables.union([constraint]))
      self._collect_unenforced(constraint.strength, False)
      self.exec_roots.append(constraint)
      self.exec_roots.extend([var_constraint \
        for var in self.redetermined_variables \
          for var_constraint in var.constraints \
            if var.determined_by is None and \
              var_constraint.is_enforced()])

  def _remove_strongest_constraint(self):
    sorted_constraints = sorted(self.unenforced_constraints, key = lambda constraint: constraint.strength, reverse = True)
    strongest_constraint = sorted_constraints[0]
    self.unenforced_constraints.remove(strongest_constraint)
    return strongest_constraint

  def _propagate_walk_strength(self, roots):
    self._new_mark()

    for constraint in self._pplan_add(roots):
      for var in constraint.selected_method.inputs:
        if var.determined_by is not None and var.determined_by.mark == self.mark:
          var.walk_strength = Strength.WEAKEST
      self._compute_walkabout_strengths(constraint)
      constraint.mark = None

  def _compute_walkabout_strengths(self, constraint):
    outs = constraint.selected_method.outputs
    for out_var in outs:
      max_strengths = [self._max_out(method, outs) for method in constraint.methods if out_var not in method.outputs]
      max_strengths.append(constraint.strength)
      out_var.walk_strength = min(max_strengths)

  def _max_out(self, method, current_outputs):
    return max([variable.walk_strength for variable in method.outputs if variable not in current_outputs])

  def _collect_unenforced(self, collection_strength, collect_equal_strength):
    self._new_mark()
    for variable in self.redetermined_variables:
      stack = [variable]
      while stack:
        cur_var = stack.pop()
        for constraint in cur_var.constraints:
          if constraint == cur_var.determined_by or constraint.mark == self.mark:
            continue
          constraint.mark = self.mark
          if constraint.is_enforced():
            stack.extend(constraint.selected_method.outputs)
          elif Strength.weaker(constraint.strength, collection_strength) or \
                (collect_equal_strength and (constraint.strength == collection_strength)):
            self.unenforced_constraints.add(constraint)

  def _any_immediate_upstream_marked(self, constraint):
    for variable in constraint.selected_method.inputs:
      if variable.determined_by is not None and variable.determined_by.mark == self.mark:
        return True
    return False

  def _execute_propagate_valid(self, constraint):
    inputs_valid = not constraint.selected_method.has_invalid_vars()

    if inputs_valid:
      constraint.selected_method.execute()

    for variable in constraint.selected_method.outputs:
      variable.valid = inputs_valid

  def _pplan_add(self, objs):
    pplan = []
    if not isinstance(objs, set) and not isinstance(objs, list):
      raise Exception("accepting only set of objs! Got %s of type %s" %(objs, type(objs)))
    for el in objs:
      el.add_to_pplan(pplan, self.mark)
    return pplan

  def _new_mark(self):
    self.marker.new_mark()
    self.mark = self.marker.mark

  def _extract_plan(self):
    good_constraints = []
    bad_constraints = []
    self._new_mark()

    for constraint in reversed(self._pplan_add(self.exec_roots)):
      if constraint.mark != self.mark:
        continue
      elif self._any_immediate_upstream_marked(constraint):
        bad_constraints.append(constraint)
      else:
        constraint.mark = None
        good_constraints.append(constraint)
    self.plan = Plan(self.exec_roots, good_constraints, bad_constraints, True)

  def _execute_plan(self):
    if self.plan.valid:
      for constraint in self.plan.good_constraints:
        self._execute_propagate_valid(constraint)
    else:
      raise ValueError("trying to execute invalid plan")
