from os.path import abspath
import logging

file_name = abspath("skypyblue.log")

logging.basicConfig(filename=file_name, filemode = "w", level = logging.DEBUG, format='%(levelname)10s - %(funcName)20s - %(message)s')

DEBUG = logging.debug
WARNING = logging.warning
ERROR = logging.error
INFO = logging.info

