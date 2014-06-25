#!/usr/bin/env python

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

from skypyblue_test import *

config = Config()
config.trace_filter = GlobbingFilter(include=[
    'skypyblue.*'
])

graphviz = GraphvizOutput()

with PyCallGraph(output=graphviz, config=config):
  skypyblue(1)
