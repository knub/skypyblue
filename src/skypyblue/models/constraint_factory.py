from skypyblue.models import Method, Constraint

class ConstraintFactory:
  def equality_constraint(self, variable1, variable2, strength):
    m1 = Method([variable1], [variable2],
      lambda v1: v1)

    m2 = Method([variable2], [variable1],
      lambda v2: v2)

    constraint = Constraint(
      lambda v1, v2: v1 == v2,
      strength,
      [variable1, variable2],
      [m1, m2])

    return constraint

  def scale_constraint(self, destination, source, scale, offset, strength):
    m1 = Method([source, scale, offset], [destination],
      lambda source, scale, offset: scale * source + offset)

    m2 = Method([destination, scale, offset], [source],
      lambda destination, scale, offset: float(destination - offset) / scale)

    constraint = Constraint(
      lambda destination, source, scale, offset: destination == scale * source + offset,
      strength,
      [destination, source, scale, offset],
      [m1, m2])

    return constraint

