from skypyblue.models import Strength, Constraint

class Variable:
  def __init__(self, name, value, system = None, walk_strength = Strength.WEAKEST):
    self.name = name
    self.value = value
    self.constraints = []
    self.determined_by = None
    self.walk_strength = walk_strength
    self.mark = None
    self.valid = True
    self.system = system

  def get_value(self):
    return self.value

  def set_value(self, value):
    self.value = value
    if self.system is not None:
      self.system.variable_changed(self)

  def remove_constraint(self,constraint):
      self.constraints=[cn for cn in self.constraints if cn!=constraint]

  def add_constraint(self, constraint):
    self.constraints.append(constraint)

  def stay(self, strength):
    if self.stay_constraint is not None:
      self.cd.remove_constraint(self.stay_constraint)

    m = Method([], [variable], lambda: variable.value)
    self.stay_constraint = Constraint(
      lambda x: True,
      strength,
      [variable], 
      [m])

    self.cs.add_constraint(self.stay_constraint)

  def removeStayConstraint(self):
    if self.stay_constraint is not None:
      self.cd.remove_constraint(self.stay_constraint)
      self.stay_constraint = None


  def __repr__(self):
    return "<Variable '%s', value: %s>" % (self.name, self.value)

