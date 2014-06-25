#!/usr/bin/env python

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

from skypyblue_test import *

config = Config()
config.trace_filter = GlobbingFilter(exclude = [
  '*listcomp*',
  '*lambda*',
  '*max_out*',
  '*enum*',
  '*skypyblue_test*',
  '*weaker*',
  '*__init__*',
  '*equality_constraint*',
  '*scale_constraint*',
  '*has_invalid_vars*',
  '*_check_constraints*',
  '*_new_mark*',
  '*pycallgraph*'
])
config.groups = True

graphviz = GraphvizOutput()

with PyCallGraph(output = graphviz, config = config):
  skypyblue(1)
