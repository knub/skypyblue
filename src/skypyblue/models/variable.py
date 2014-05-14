from walkabout_strengths import *

class Variable:
  def __init__(self, value, walk_strength = WalkaboutStrength.WEAKEST):
    self.value = value
    self.constraints = []
    self.determined_by = None
    self.walk_strength = walk_strength
    self.mark = None
    self.valid = True

