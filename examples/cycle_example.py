import sys
sys.path.append("../src")

from skypyblue.core import ConstraintSystem
from skypyblue.models import Method, Constraint, Strength, ConstraintFactory

cs = ConstraintSystem()
a, b, c, d = cs.create_variables(["a", "b", "c", "d"], [1, 2, 3, 0])
one = cs.create_variable("1", 1)

cn1 = ConstraintFactory().scale_constraint(b, a, one, one, Strength.STRONG)
cn2 = ConstraintFactory().scale_constraint(c, b, one, one, Strength.STRONG)
cn3 = ConstraintFactory().scale_constraint(a, c, one, one, Strength.STRONG)
cn4 = ConstraintFactory().scale_constraint(a, d, one, one, Strength.STRONG)



for var in [a, b, c, d]:
  print var.name, var.get_value(), var.valid

for cn in [cn1, cn2, cn3, cn4]:
  cs.add_constraint(cn)

print
for var in [a, b, c, d]:
  print var.name, var.get_value(), var.valid



# for cn in [cn1, cn2, cn3, cn4]:

