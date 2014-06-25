
cs = ConstraintSystem()

# p = Point(10,15)

v1 = Variable("v1", 15, cs)
v2 = Variable("v2", 15, cs)
v3 = Variable("v3", 15, cs)
v4 = Variable("v4", 10, cs)

cs.stay(v4, Strength.WEAK)

# v1 + v2 = v3, v1 - v2 = v4
m12_34 = Method([v1, v2], [v3, v4],
  lambda v1, v2: (v1 + v2 , v1 - v2))

m34_12 = Method([v3, v4], [v1, v2],
  lambda v3, v4: (v3 + v4) / 2 , (v3 - v4) / 2)

cn1 = Constraint(
  lambda v1, v2, v3, v4: v1 + v2 == v3 and v1 - v2 == v4,
  Strength.STRONG, 
  [v1, v2, v3, v4], 
  [m12_34, m34_12])

cs.add_constraint(cn1) # sets v3 to 30 and v4 to 0

v3.set_value(10) # observer/listener?
v1.get_value() # 5
v2.get_value() # 5

# Questions
# - Example? Sophisticated test case?
