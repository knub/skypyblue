from models.strengths import *

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

  def remove_constraint(self,constraint):
      self.constraints=[cn for cn in self.constraints if cn!=constraint]

  def add_constraint(self, constraint):
    self.constraints.append(constraint)

