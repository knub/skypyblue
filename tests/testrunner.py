#!/usr/bin/env python3
"""
Usage:
  ./testrunner.py                     -> executes all tests
  ./testrunner.py <TestCaseClass>     -> executes only tests from this testcase
"""

if __name__ != "__main__": exit()

import unittest, sys
sys.path.append("../src")
sys.path.append("./performance")


from constraint_system_tests import *
from variable_tests import *
from helper_method_tests import *
from mvine_tests import *
from exec_tests import *
from midpoint_tests import *
from extended_midpoint_tests import *
from update_method_graph_tests import *
from constraint_tests import *
from constraint_factory_tests import *
from cycle_tests import *
from chain_tests import *

# from benchmark import *
# run_benchmark([2, 0, 50])

unittest.main()
