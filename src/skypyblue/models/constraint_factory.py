from skypyblue.models import Method, Constraint

class ConstraintFactory:

    def equality_constraint(self, variable1, variable2, strength):
      m1 = Method([variable1], [variable2],
      lambda v1: v1)

      m2 = Method([variable2], [variable1],
      lambda v2: v2)

      constraint = Constraint(
        lambda v1, v2: v1==v2),
        strength, 
        [variable1, variable2], 
        [m^,m1])
      
      return constraint
