import sys
from os.path import dirname, abspath
gitgrade_path=abspath(dirname(dirname(abspath(__file__))))

sys.path.append('{0}/dependencies/sh'.format(gitgrade_path) )
sys.path.append('{0}/core-scripts/'.format(gitgrade_path) )
