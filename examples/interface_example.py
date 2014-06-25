
cs = ConstraintSystem()

# p = Point(10,15)
# v1 = cs.create_variable("v1", p, mutable = True)

v1 = cs.create_variable("v1", 15)
v2 = cs.create_variable("v2", 15)
v3 = cs.create_variable("v3", 15)
v4 = cs.create_variable("v4", 10)

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
