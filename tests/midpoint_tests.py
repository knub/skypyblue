import unittest
from constraint_system import ConstraintSystem
from models import Constraint, Strength, Method

class Point(object):
  def __init__(self, x, y):
    self.X = x
    self.Y = y

  def distance(self, other):
    dx = self.X - other.X
    dy = self.Y - other.Y
    return math.sqrt(dx**2 + dy**2)

  def isMidpoint(self, point1, point2):
    return self.X == (point1.X+point2.X)/2 and self.Y == (point1.Y+point2.Y)/2

  def print_position(self):
    print(self.X,'@',self.Y)

class MidpointTestClass(unittest.TestCase):
  __name__ = "MidpointTestClass"
  def setUp(self):
    self.constraint_system =ConstraintSystem()
    self.point1 = self.constraint_system.create_variable("Point 1", Point(4,10))
    self.point2 = self.constraint_system.create_variable("Point 2", Point(10,30))
    self.midpoint = self.constraint_system.create_variable("midpoint", Point(0,0))

    mMp = Method([self.point1, self.point2], [self.midpoint],
      lambda p1, p2: Point((p1.X + p2.X)/2 , (p1.Y + p2.Y)/2))

    mP1 = Method([self.midpoint, self.point2], [self.point1],
      lambda mp, p2: Point((2*mp.X - p2.X)/2 , (2*mp.Y - p2.Y)/2))

    mP2 = Method([self.midpoint, self.point1], [self.point2],
      lambda mp, p1: Point((2*mp.X - p1.X)/2 , (2*mp.Y - p1.Y)/2))


    constraint = Constraint(
        lambda point1, point2, midpoint: midpoint.isMidpoint(point1, point2),
        Strength.STRONG, 
        [self.point1, self.point2, self.midpoint], 
        [mMp, mP1, mP2])

    self.constraint_system.add_constraint(constraint)


  def test_contraint(self):
    midpoint = self.midpoint.get_value()
    point1 = self.point1.get_value()
    point2 = self.point2.get_value()
    self.assertTrue(midpoint.isMidpoint(point1,point2))

  def test_change_point1(self):
    self.point1.set_value(Point(0,0))
    self.constraint_system.exec_from_roots([self.point1])
    point1 = self.point1.get_value()
    self.test_contraint()
    self.assertEqual(point1.X, 0)
    self.assertEqual(point1.Y, 0)

  @unittest.skip
  def test_change_midpoint(self):
    self.midpoint.set_value(Point(0,0))
    self.constraint_system.exec_from_roots([self.midpoint])
    midpoint = self.midpoint.get_value()
    self.test_contraint()
    self.assertEqual(midpoint.X, 0)
    self.assertEqual(midpoint.Y, 0)
