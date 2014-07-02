from distutils.core import setup
setup(
  name='skypyblue',
  version='0.1.0',
  packages=['skypyblue', 'skypyblue.core', 'skypyblue.models'],
  install_requires=['enum34'],
  test_requires=['mock']
)
