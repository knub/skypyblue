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

class MidpointTestClass(unittest.TestCase):
  def setUp(self):
    self.constraintSystem =ConstraintSystem()
    self.point1 = cs.create_variable("Point 1", Point(4,10))
  self.point2 = cs.create_variable("Point 2", Point(10,30))
  self.midpoint = cs.create_variable("midpoint", Point(0,0))

  mMp = Method([point1, point2], [midpoint],
    lambda p1, p2: Point((p1.X + p2.X)/2 , (p1.Y + p2.Y)/2)

  mP1 = Method([midpoint, point2], [point1],
    lambda mp, p2: Point((2*mp.X - p2.X)/2 , (2*mp.Y - p2.Y)/2)

  mP2 = Method([midpoint, point1], [point2],
    lambda mp, p1: Point((2*mp.X - p1.X)/2 , (2*mp.Y - p1.Y)/2)


  constraint = Constraint(
      lambda point1, point2, midpoint: midpoint.isMidpoint(point1, point2),
      WalkaboutStrength.STRONG, 
      [point1, point2, midpoint], 
      [mMp, mP1, mP2])

  cs.add_constraint(constraint)


  def test_contraint(self):
    midpoint = self.midpoint.getValue()
    point1 = self.point1.getValue()
    point2 = self.point1.getValue()
    self.assertTrue(midpoint.isMidpoint(point1,point2))

    def test_change_point1(self):
      self.point1.setValue(Point(0,0))
    point1 = self.point1.getValue()
    self.test_contraint()
    self.assertEqual(point1.X, 0)
    self.assertEqual(point1.Y, 0)

  def test_change_midpoint(self):
      self.midpoint.setValue(Point(0,0))
      midpoint = self.midpoint.getValue()
    self.test_contraint()
    self.assertEqual(midpoint.X, 0)
    self.assertEqual(midpoint.Y, 0)