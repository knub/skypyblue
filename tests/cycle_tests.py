
from unittest import TestCase
from skypyblue.core import ConstraintSystem, CycleException, logger
from skypyblue.models import Method, Constraint, Strength, ConstraintFactory, Variable

class CycleTest(TestCase):
  def setUp(self):
    self.cs = ConstraintSystem()

  def test_cycle_should_be_detected(self):
    a, b, c, d = self.cs.create_variables(["a", "b", "c", "d"], [1, 2, 3, 0])
    one = Variable("1", 1, self.cs)

    cn1 = ConstraintFactory().scale_constraint(b, a, one, one, Strength.STRONG)
    cn2 = ConstraintFactory().scale_constraint(c, b, one, one, Strength.STRONG)
    cn3 = ConstraintFactory().scale_constraint(a, c, one, one, Strength.STRONG)
    cn4 = ConstraintFactory().scale_constraint(a, d, one, one, Strength.STRONG)

    with self.assertRaises(CycleException) as e:
      for cn in [cn1, cn2, cn3, cn4]:
        self.cs.add_constraint(cn)


  def test_cycle_variables_should_be_invalid(self):
    a, b, c, d = self.cs.create_variables(["a", "b", "c", "d"], [1, 2, 3, 0])
    one = Variable("1", 1, self.cs)

    cn1 = ConstraintFactory().scale_constraint(b, a, one, one, Strength.STRONG, "cn1")
    cn2 = ConstraintFactory().scale_constraint(c, b, one, one, Strength.STRONG, "cn2")
    cn3 = ConstraintFactory().scale_constraint(a, c, one, one, Strength.STRONG, "cn3")
    cn4 = ConstraintFactory().scale_constraint(a, d, one, one, Strength.STRONG, "cn4")

    try:
      for cn in [cn1, cn2, cn3, cn4]:
        self.cs.add_constraint(cn)
    except CycleException as c_exc:
      self.assertEqual(set([cn1, cn2, cn3]), c_exc.cycled_constraints)
      for var in c_exc.cycled_variables:
        self.assertFalse(var.valid, "%s should be invalid" %(var) )
    else:
      raise Exception("should have risen an CycleException")


  def test_should_not_detect_a_cycle(self):
    a, b, c = self.cs.create_variables(["a", "b", "c"], [1, 2, 3])

    m1 = Method([a, c], [b], lambda a,c: a + c)
    m2 = Method([b, c], [a], lambda b,c: b - c)

    cn = Constraint(lambda a,b,c: a + c == b, Strength.STRONG, [a, b, c], [m1, m2], "cn1")

    self.cs.add_constraint(cn)
    a.stay()
    b.set_value(4)
    c.set_value(8)
