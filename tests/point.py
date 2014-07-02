import math

class Point(object):
  def __init__(self, x, y):
    self.X = x
    self.Y = y

  def distance(self, other):
    dx = self.X - other.X
    dy = self.Y - other.Y
    return math.sqrt(dx ** 2 + dy ** 2)

  def is_midpoint(self, point1, point2):
    return self.X == (point1.X + point2.X) / 2 and self.Y == (point1.Y + point2.Y) / 2

  def print_position(self):
    print(self.X, '@', self.Y)

  def __repr__(self):
    return "(%s, %s)" % (self.X, self.Y)

  def equals(self, point):
    return self.X == point.X and self.Y == point.Y
