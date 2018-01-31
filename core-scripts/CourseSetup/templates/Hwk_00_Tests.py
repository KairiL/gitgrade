import sys
import os
import logging
import subprocess
import shutil # this is a new module to copy file
#import pexpect

from sh import cat, ls, cp, mv
import config
sys.path.append ('{0}/core-scripts/'.format(config.gitgrade_path))
import Test


# Define the tests used in feedback and grading
# --------------------------------------------------
'''
These are sample tests for a new course
It is suggested that you begin with these simple tests to get yourself and 
your students adjusted to the new grading script system.  Additional tests 
and tools for creating more tests are contained within core-scripts/Test.py
'''
#does the directory "Hwk_00" exist in the students' team repository?
dir_exists = Test.DirectoryExists("Hwk_00", 10)
#does the file "Hwk_00/Do_Nothing.py" exist in the students' team repository?
file_exists = Test.FileExists("Hwk_00/Do_nothing.py", 10)
