import unittest
from skypyblue.core import ConstraintSystem
from skypyblue.models import Constraint, Strength, Method, Variable
from point import Point

class MidpointTest(unittest.TestCase):
  __name__ = "MidpointTest"
  def setUp(self):
    self.constraint_system = ConstraintSystem()
    self.point1 = Variable("Point 1", Point(4, 10), self.constraint_system)
    self.point2 = Variable("Point 2", Point(10, 30), self.constraint_system)
    self.midpoint = Variable("midpoint", Point(0, 0), self.constraint_system)

    mMp = Method([self.point1, self.point2], [self.midpoint],
      lambda p1, p2: Point((p1.X + p2.X) / 2 , (p1.Y + p2.Y) / 2))

    mP1 = Method([self.midpoint, self.point2], [self.point1],
      lambda mp, p2: Point((2 * mp.X - p2.X) , (2 * mp.Y - p2.Y)))

    mP2 = Method([self.midpoint, self.point1], [self.point2],
      lambda mp, p1: Point((2 * mp.X - p1.X) , (2 * mp.Y - p1.Y)))


    constraint = Constraint(
        lambda point1, point2, midpoint: midpoint.is_midpoint(point1, point2),
        Strength.STRONG,
        [self.point1, self.point2, self.midpoint],
        [mMp, mP1, mP2])

    self.constraint_system.add_constraint(constraint)


  def test_contraint(self):
    midpoint = self.midpoint.get_value()
    point1 = self.point1.get_value()
    point2 = self.point2.get_value()
    self.assertTrue(midpoint.is_midpoint(point1,point2))

  def test_change_point1(self):
    self.point1.set_value(Point(0, 0))
    point1 = self.point1.get_value()
    self.test_contraint()
    self.assertEqual(point1.X, 0)
    self.assertEqual(point1.Y, 0)

  def test_change_midpoint(self):
    self.midpoint.set_value(Point(0, 0))
    midpoint = self.midpoint.get_value()
    self.test_contraint()
    self.assertEqual(midpoint.X, 0)
    self.assertEqual(midpoint.Y, 0)

  def test_change_several_points(self):
    self.midpoint.set_value(Point(0, 0))
    self.point1.set_value(Point(10, 10))
    self.point2.set_value(Point(50, 50))
    point2 = self.point2.get_value()
    self.test_contraint()
    self.assertEqual(point2.X, 50)
    self.assertEqual(point2.Y, 50)

  def test_change_two_points_at_the_same_time(self):
    self.constraint_system.change_variable_values(
        [self.point1, self.point2],
        [Point(0, 0), Point(20, 20)]
      )
    point1 = self.point1.get_value()
    point2 = self.point2.get_value()
    self.test_contraint()
    self.assertEqual(point1.X, 0)
    self.assertEqual(point1.Y, 0)
    self.assertEqual(point2.X, 20)
    self.assertEqual(point2.Y, 20)

