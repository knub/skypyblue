import unittest
import math
from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Strength, Method, Variable
from point import Point

class ExtendedMidpointTest(unittest.TestCase):
  __name__ = "ExtendedMidpointTest"
  def setUp(self):
    self.constraint_system = ConstraintSystem()
    self.point1 = Variable("Point 1", Point(4, 10), self.constraint_system)
    self.point2 = Variable("Point 2", Point(10, 30), self.constraint_system)
    self.point3 = Variable("Point 3", Point(50, 20), self.constraint_system)
    self.point4 = Variable("Point 4", Point(100, 30), self.constraint_system)
    self.midpoint = Variable("midpoint", Point(0, 0), self.constraint_system)

    mpmp3p4 = Method([self.midpoint, self.point3, self.point4], [self.point1, self.point2],
      lambda pm, p3, p4: (
        Point(
          pm.X - (p4.X - p3.X),
          pm.Y - (p4.Y - p3.Y)
        ),
        Point(
          pm.X + (p4.X - p3.X),
          pm.Y + (p4.Y - p3.Y)
        )
      )
    )
    mp1pmp3 = Method([self.point1, self.midpoint, self.point3], [self.point2, self.point4],
      lambda p1, pm, p3: (
        Point(
          2 * pm.X - p1.X,
          2 * pm.Y - p1.Y
        ),
        Point(
          p3.X + (pm.X - p1.X),
          p3.Y + (pm.Y - p1.Y)
        )
      )
    )
    mpmp2p4 = Method([self.midpoint, self.point2, self.point4], [self.point1, self.point3],
      lambda pm, p2, p4: (
        Point(
          2 * pm.X - p2.X,
          2 * pm.Y - p2.Y
        ),
        Point(
          p4.X + (pm.X - p2.X),
          p4.Y + (pm.Y - p2.Y)
        )
      )
    )

    constraint = Constraint(
      lambda p1, p2, p3, p4, pm: pm.is_midpoint(p1, p2) and
                           p1.distance(pm) == p3.distance(p4),
      Strength.STRONG,
      [self.point1, self.point2, self.point3, self.point4, self.midpoint],
      [mpmp3p4, mp1pmp3, mpmp2p4])

    self.constraint_system.add_constraint(constraint)

    self.point3.stay()
    self.point4.stay()

  def test_contraint(self):
    pm = self.midpoint.get_value()
    p1 = self.point1.get_value()
    p2 = self.point2.get_value()
    p3 = self.point3.get_value()
    p4 = self.point4.get_value()
    self.assertTrue(pm.is_midpoint(p1,p2))
    self.assertTrue(p1.distance(pm) == p3.distance(p4))

  def test_change_point1(self):
    pm_old = self.midpoint.get_value()
    self.point1.set_value(Point(0, 0))
    self.test_contraint()
    self.assertTrue(self.point1.get_value().equals(Point(0,0)))
    self.assertTrue(self.midpoint.get_value().equals(pm_old))

  def test_change_midpoint(self):
    self.midpoint.set_value(Point(0, 0))
    midpoint = self.midpoint.get_value()
    self.test_contraint()
    self.assertTrue(self.midpoint.get_value(), Point(0,0))

  def test_change_point3(self):
    pm_old = self.midpoint.get_value()
    self.point3.set_value(Point(0, 0))
    self.test_contraint()
    self.assertTrue(self.point3.get_value().equals(Point(0,0)))
    self.assertTrue(self.midpoint.get_value().equals(pm_old))
