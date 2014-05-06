import unittest
from somemodule import some_func, some_other_func

class SomeTestClass(unittest.TestCase):
  def test_the_function(self):
    self.assertEquals(some_func(2), 4)

class SomeOtherTestClass(unittest.TestCase):
  def test_the_other_function(self):
    self.assertEquals(some_other_func(4), 2)
    with self.assertRaises(ValueError):
      some_other_func(-4)
