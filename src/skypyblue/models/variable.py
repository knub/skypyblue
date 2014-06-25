from skypyblue.models import Strength

class Variable:
  def __init__(self, name, value, system, walk_strength = Strength.WEAKEST):
    self.name = name
    self._value = value
    self.constraints = set()
    self.determined_by = None
    self.walk_strength = walk_strength
    self.mark = None
    self.valid = True
    self.system = system
    self.stay_constraint = None
    system.variables.append(self)

  def add_to_pplan(self, pplan, done_mark):
    for cn in self.constraints:
      if cn != self.determined_by:
        cn.add_to_pplan(pplan, done_mark)
    return pplan

  def get_value(self):
    return self._value

  def set_value(self, value, triggerChange = True):
    self._value = value
    if self.system is not None and triggerChange:
      self.system.variable_changed(self)

  def remove_constraint(self, constraint):
    self.constraints.remove(constraint)# = [cn for cn in self.constraints if cn != constraint]
    # print self, self.constraints

  def add_constraint(self, constraint):
    self.constraints.add(constraint)
    # print self, self.constraints

  def stay(self, strength = Strength.WEAK):
    if self.stay_constraint is not None:
      self.system.remove_constraint(self.stay_constraint)

    self.stay_constraint = self.system.add_stay_constraint(self, strength)

  def remove_stay_constraint(self):
    if self.stay_constraint is not None:
      self.system.remove_constraint(self.stay_constraint)
      self.stay_constraint = None


  def __repr__(self):
    return "<Variable '%s', value: %s>" % (self.name, self._value)

