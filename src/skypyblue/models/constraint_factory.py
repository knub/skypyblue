from skypyblue.models import Method, Constraint

class ConstraintFactory(object):
  @staticmethod
  def equality_constraint(variable1, variable2, strength, name = ""):
    """Creates an equality constraint, i.e. two variables are always equal."""
    m1 = Method([variable1], [variable2],
      lambda v1: v1)

    m2 = Method([variable2], [variable1],
      lambda v2: v2)

    constraint = Constraint(
      lambda v1, v2: v1 == v2,
      strength,
      [variable1, variable2],
      [m1, m2], name)

    return constraint

  @staticmethod
  def scale_constraint(destination, source, scale, offset, strength, name = ""):
    """Creates a linear equation constraint, i.e. destination = scale * source + offset."""
    m1 = Method([source, scale, offset], [destination],
      lambda source, scale, offset: scale * source + offset)

    m2 = Method([destination, scale, offset], [source],
      lambda destination, scale, offset: float(destination - offset) / scale)

    constraint = Constraint(
      lambda destination, source, scale, offset: destination == scale * source + offset,
      strength,
      [destination, source, scale, offset],
      [m1, m2], name)

    return constraint
