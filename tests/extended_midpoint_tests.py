import unittest
import math
from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Strength, Method

class Point(object):
  def __init__(self, x, y):
    self.X = x
    self.Y = y

  def distance(self, other):
    dx = self.X - other.X
    dy = self.Y - other.Y
    return math.sqrt(dx ** 2 + dy ** 2)

  def isMidpoint(self, point1, point2):
    return self.X == (point1.X + point2.X) / 2 and self.Y == (point1.Y + point2.Y) / 2

  def print_position(self):
    print(self.X, '@', self.Y)

  def equals(self, point):
    return self.X==point.X and self.Y==point.Y

  def __repr__(self):
    return "(%s, %s)" % (self.X, self.Y)

class MidpointTestClass(unittest.TestCase):
  __name__ = "MidpointTestClass"
  def setUp(self):
    self.constraint_system =ConstraintSystem()
    self.point1 = self.constraint_system.create_variable("Point 1", Point(4, 10))
    self.point2 = self.constraint_system.create_variable("Point 2", Point(10, 30))
    self.point3 = self.constraint_system.create_variable("Point 3", Point(50, 20))
    self.point4 = self.constraint_system.create_variable("Point 4", Point(100, 30))
    self.midpoint = self.constraint_system.create_variable("midpoint", Point(0, 0))

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
                           p1.distance(pm) == p3.length(p4),
      Strength.STRONG,
      [self.point1, self.point2, self.point3, self.point4,self.midpoint],
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
    self.assertTrue(pm.isMidpoint(p1,p2))
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
