# redirect stdout and stderr to files in this dir
import sys
sys.stdout = open('C:\\stdout.txt', 'w')
sys.stderr = open('C:\\stderr.txt', 'w')

from .Pancake3D_eae430b521c411efa291f83441a96bd5 import Pancake3D_eae430b521c411efa291f83441a96bd5
