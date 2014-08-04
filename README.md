#skypyblue

[![Build Status](https://travis-ci.org/knub/skypyblue.svg)](https://travis-ci.org/knub/skypyblue)

Implementation of the [SkyBlue](https://www.cs.washington.edu/research/constraints/solvers/skyblue-tr-92.html) constraint solver in Python.

Tested with Python2.7, Python3.x and Pypy.

### Usage

#### Base Classes
**ConstraintSystem, Variable, Method, Constraint, Strength** 

```python
from skypyblue.models import ConstraintSystem, Variable, Method, Constraint, Strength

cs = ConstraintSystem()

v1 = Variable("v1", 1, cs)
v2 = Variable("v2", 2, cs)
m1 = Method([v1], [v2], lambda v1: v1)

m2 = Method([v2], [v2], lambda v2: v2)

constraint = Constraint(
  lambda v1, v2: v1 == v2,
  Strength.STRONG,
  [v1, v2], [m1, m2])

cs.add_constraint(constraint)

v1.get_value() # => 1
v2.get_value() # => 1
```

#### ConstraintFactory

```python
from skypyblue.models import ConstraintSystem, Variable, ConstraintFactory, Strength

cs = ConstraintSystem()

v1 = Variable("v1", 1, cs)
v2 = Variable("v2", 2, cs)
constraint = ConstraintFactory.equality_constraint(v1, v2, Strength.STRONG)

cs.add_constraint(constraint)

v1.get_value() # => 1
v2.get_value() # => 1
```

### Graphical Demo - requires [pygame](http://www.pygame.org/) package, only Python2.7 and Python3.x
```
cd examples
python midpoint_example.py
```

### Testing
```
cd tests
python testrunner.py
```

### Performance
Benchmark does two tests: chain and projection test. It runs python implementation of DeltaBlue first and then our implementation. Parameters for the benchmark script: `python benchmark.py #rounds #warmups #constraints`
```
cd tests/performance
python benchmark.py 5 15 200
```
### Numbers
All times are in *ms*.

|**Chain**| python2 | python3 | pypy |**Projection**| python2 | python3 | pypy |
|     ---    |   ---  |  ---  |  --- | --- | --- | --- | --- |
| **Delta Blue** | 24  | 26 | 0 | | 13 | 16 | 6 |
|            | 26  | 26 | 1 | | 15 | 16 | 3 |
|            | 27  | 26 | 1 | | 15 | 18 | 3 |
|            | 25  | 25 | 3 | | 17 | 18 | 3 |
|            | 26  | 26 | 0 | | 15 | 16 | 3 |
| **Skypyblue**  | 412 | 499 | 82 | | 32 | 66 | 5 |
|            | 427 | 491 | 77 | | 62 | 38 | 5 |
|            | 406 | 496 | 65 | | 32 | 39 | 9 |
|            | 417 | 493 | 70 | | 33 | 39 | 6 |
|            | 412 | 496 | 78 | | 32 | 38 | 19 |


### Deployment on [PyPI](https://pypi.python.org/pypi/skypyblue)
``` 
cd src
make deploy
```

OR

``` 
cd src
python setup.py sdist upload 
```

### Bugs, Problems?

stefan.bunk@..
daniel.kurzynski@..
dimitri.korsch@

..@student.hpi.uni-potsdam.de

