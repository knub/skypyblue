from skypyblue.models import Method, Constraint

class ConstraintFactory:

    def equality_constraint(self, variable1, variable2, strength):
      m1 = Method([variable1], [variable2],
        lambda v1: v1)

      m2 = Method([variable2], [variable1],
        lambda v2: v2)

      constraint = Constraint(
        lambda v1, v2: v1==v2,
        strength, 
        [variable1, variable2], 
        [m1,m2])
      
      return constraint

    def scale_constraint(self, variable1, variable2, variableX, variableY):
      m1 = Method([variable2, variableX, variableY], [variable1],
        lambda v2,vx,vy: vx*v2+vy)

      m2 = Method([variable1, variableX, variableY], [variable2],
        lambda v1,vx,vy: (v1-vy)/vx)

      constraint = Constraint(
        lambda v1, v2, vx, vy: v1==vx*v2+vy,
        strength, 
        [variable1, variable2, variableX, variableY], 
        [m1,m2])
      
      return constraint

