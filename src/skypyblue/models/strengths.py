try:
  from enum import IntEnum
except ImportError as e:
  print("Your python version does not provides the enum module. Please install enum34 package(eg. with 'pip install enum34')!")
  raise e

class Strength(IntEnum):
  WEAKEST, WEAK, MEDIUM, STRONG, REQUIRED = range(5)

  @staticmethod
  def weaker(strength1, strength2):
    return strength1 < strength2

  @staticmethod
  def stronger(strength1, strength2):
    return strength1 >= strength2

class InternalStrength(IntEnum):
  FORCED = 6

  @staticmethod
  def weaker(strength1, strength2):
    return strength1 < strength2

  @staticmethod
  def stronger(strength1, strength2):
    return strength1 >= strength2

