
from unittest import TestCase
from skypyblue.core import ConstraintSystem, CycleException, logger
from skypyblue.models import Method, Constraint, Strength, ConstraintFactory, Variable

class CycleTest(TestCase):
  def setUp(self):
    self.constraint_system = ConstraintSystem()

  def test_cycle_should_be_detected(self):
    a, b, c, d = self.constraint_system.create_variables(["a", "b", "c", "d"], [1, 2, 3, 0])
    one = Variable("1", 1, self.constraint_system)

    constraint1 = ConstraintFactory().scale_constraint(b, a, one, one, Strength.STRONG)
    constraint2 = ConstraintFactory().scale_constraint(c, b, one, one, Strength.STRONG)
    constraint3 = ConstraintFactory().scale_constraint(a, c, one, one, Strength.STRONG)
    constraint4 = ConstraintFactory().scale_constraint(a, d, one, one, Strength.STRONG)

    with self.assertRaises(CycleException) as e:
      for constraint in [constraint1, constraint2, constraint3, constraint4]:
        self.constraint_system.add_constraint(constraint)


  def test_cycle_variables_should_be_invalid(self):
    a, b, c, d = self.constraint_system.create_variables(["a", "b", "c", "d"], [1, 2, 3, 0])
    one = Variable("1", 1, self.constraint_system)

    constraint1 = ConstraintFactory().scale_constraint(b, a, one, one, Strength.STRONG, "constraint1")
    constraint2 = ConstraintFactory().scale_constraint(c, b, one, one, Strength.STRONG, "constraint2")
    constraint3 = ConstraintFactory().scale_constraint(a, c, one, one, Strength.STRONG, "constraint3")
    constraint4 = ConstraintFactory().scale_constraint(a, d, one, one, Strength.STRONG, "constraint4")

    try:
      for constraint in [constraint1, constraint2, constraint3, constraint4]:
        self.constraint_system.add_constraint(constraint)
    except CycleException as c_exc:
      self.assertEqual(set([constraint1, constraint2, constraint3]), set(c_exc.cycled_constraints))
      for variable in c_exc.cycled_variables:
        self.assertFalse(variable.valid, "%s should be invalid" %(variable) )
    else:
      raise Exception("should have risen an CycleException")


  def test_should_not_detect_a_cycle(self):
    a, b, c = self.constraint_system.create_variables(["a", "b", "c"], [1, 2, 3])

    method1 = Method([a, c], [b], lambda a,c: a + c)
    method2 = Method([b, c], [a], lambda b,c: b - c)

    constraint = Constraint(lambda a,b,c: a + c == b, Strength.STRONG, [a, b, c], [method1, method2], "constraint1")

    self.constraint_system.add_constraint(constraint)
    a.stay()
    b.set_value(4)
    c.set_value(8)
