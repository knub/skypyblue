#!/usr/bin/env python3
"""
Usage: 
  ./testrunner.py                     -> executes all tests
  ./testrunner.py <TestCaseClass>     -> executes only tests from this testcase
"""

if __name__ != "__main__": exit()

import unittest, sys
sys.path.append("../src/skypyblue")


from constraint_system_tests import *
from variable_tests import *

unittest.main()

