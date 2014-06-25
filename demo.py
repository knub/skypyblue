cs = ConstraintSystem()

v1 = Variable("v1", 1, cs)
v2 = Variable("v2", 2, cs)
m1 = Method([v1], [v2],
  lambda v1: v1)

m2 = Method([v2], [v2],
  lambda v2: v2)

constraint = Constraint(
  lambda v1, v2: v1 == v2,
  Strength.STRONG,
  [v1, v2],
  [m1, m2])

cs.add_constraint(constraint)

v1.get_value() # => 1
v2.get_value() # => 1

=================

cs = ConstraintSystem()

v1 = Variable("v1", 1, cs)
v2 = Variable("v2", 2, cs)
constraint = ConstraintFactory.equality_constraint(v1, v2, Strength.STRONG)

cs.add_constraint(constraint)

v1.get_value() # => 1
v2.get_value() # => 1
