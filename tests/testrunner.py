#!/usr/bin/env python3
"""
Usage: 
  ./testrunner.py                     -> executes all tests
  ./testrunner.py <TestCaseClass>     -> executes only tests from this testcase
"""

if __name__ != "__main__": exit()

import unittest, sys
sys.path.append("../src")


from sometestmodule import *

unittest.main()

