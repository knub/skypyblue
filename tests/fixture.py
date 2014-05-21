from constraint_system import ConstraintSystem
from models import Variable, Strength, Constraint, Variable

class Fixture:
  def __init__(self):
    self.constraint_system = ConstraintSystem()
    self.a = self.constraint_system.create_variable("a", 1)
    self.b = self.constraint_system.create_variable("b", 2)
    self.c = self.constraint_system.create_variable("c", 3)

    self.a_equals_b_plus_2_contraint = self.create_a_equals_b_plus_2_contraint()
    self.a_equals_c_minus_1_contraint = self.create_a_equals_c_minus_1_contraint()
    self.a_plus_b_equals_c_constraint = self.create_a_plus_b_equals_c_constraint()


  def create_a_equals_b_plus_2_contraint(self):
    mA = Method([self.a], [self.b],
    lambda a: b+2)

    mB = Method([self.b], [self.a],
    lambda b: a-2)

    return Constraint(
      lambda a, b: a==b+2,
      WalkaboutStrength.STRONG, 
      [self.a, self.b], 
      [mA,mB])

  def create_a_equals_c_minus_1_contraint(self):
    mA = Method([self.a], [self.c],
    lambda a: c-1)

    mC = Method([self.c], [self.a],
    lambda c: a+1)

    return Constraint(
      lambda a, c: a==c-1,
      WalkaboutStrength.STRONG, 
      [self.a, self.c], 
      [mA,mC])

  def create_a_plus_b_equals_c_constraint(self):
    mC = Method([self.a,self.b], [self.c],
    lambda a,b: a+b)

    mB = Method([self.a,self.c], [self.b],
    lambda a,c: c-a)

    mA = Method([self.b,self,c], [self.a],
    lambda b,c: c-b)

    return Constraint(
      lambda a,b,c: a+b==c,
      WalkaboutStrength.STRONG, 
      [self.a, self.b, self.c], 
      [mA,mB,mC])

  def simple_constraint_system(self):
    self.constraint_system.add_constraint(self.a_equals_b_plus_2_contraint)
    self.constraint_system.add_constraint(self.a_equals_c_minus_1_contraint)
    return self.constraint_system
