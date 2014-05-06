import math

def some_func(x):
  return x*x

def some_other_func(x):
  if x < 0: raise ValueError("values may not be negative")
  return int(math.sqrt(x))