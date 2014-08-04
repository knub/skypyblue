from __future__ import division

import sys
sys.path.append("../src")
sys.path.append("../tests")

from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Strength, Variable, Method

cs = ConstraintSystem()

v1 = Variable("v1", 16, cs)
v2 = Variable("v2", 16, cs)
v3 = Variable("v3", 16, cs)
v4 = Variable("v4", 10, cs)

v4.stay()

# v1 + v2 = v3, v1 - v2 = v4
m12_34 = Method([v1, v2], [v3, v4],
  lambda v1, v2: (v1 + v2 , v1 - v2))

m34_12 = Method([v3, v4], [v1, v2],
  lambda v3, v4: ((v3 + v4) / 2 , (v3 - v4) / 2))

cn1 = Constraint(
  lambda v1, v2, v3, v4: v1 + v2 == v3 and v1 - v2 == v4,
  Strength.STRONG, 
  [v1, v2, v3, v4], 
  [m12_34, m34_12])

cs.add_constraint(cn1)

def print_values():
  print("v1 = " + str(v1.get_value()))
  print("v2 = " + str(v2.get_value()))
  print("v3 = " + str(v3.get_value()))
  print("v4 = " + str(v4.get_value()))
print("Constraint: v1 + v2 = v3, v1 - v2 = v4.")
print_values()

print("Set v1 to 5.")
v1.set_value(5)
print_values()

print("Set v2 to 8.")
v2.set_value(8)
print_values()

print("Set v3 to 10.")
v3.set_value(10)
print_values()

print("Set v4 to 2.")
v4.set_value(2)
print_values()
