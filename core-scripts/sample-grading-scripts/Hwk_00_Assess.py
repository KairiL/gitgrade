import os, logging, datetime, sys, subprocess, csv
import config
sys.path.append('{0}/dependencies/sh'.format(config.gitgrade_path) )
from sh import git, cat, echo
sys.path.append ('{0}/core-scripts/'.format(config.gitgrade_path) )
import Test
import Action
import Course
import Hwk_00_Tests

class Hwk_00_Assess(Action.Assessment):
    '''Assessment for Hwk 00 in Rl 101'''

    def __init__(self):
        Action.Feedback.__init__(self, Course.course() )

        # sub directory in Course.grading_dir
        grading_sub_dir = "Hwk_00_Assessment"
        self.grading_dir = self.course.grading_home_dir + "/" + grading_sub_dir
        self.hwk_num = "00"
        self.isAssessment = True
        self.rmRepo = False
        
        # Define course tests for this feedback.
        # --------------------------------------------------
        current_date = datetime.datetime.now()
        self.timestamp = current_date.strftime("%B %d, %H:%M:%S %p")
        print ("Timestamp: {0}\n\n".format(self.timestamp))

        self.tests = Test.SequenceTest ([ 
                       Test.Message("### Assessment for Homework 0"),
                       Test.TimestampMessage(),
                       Test.FailingSequenceTest ([ 
                         Hwk_00_Tests.dir_exists, 
                         Hwk_00_Tests.file_exists,

                       ]) 
        ])

# Status:
# If the feedbck file doesn't exist, we can commit an empty file, even though it 
# is not empty in the repo.

# What works:
# -----------
# If the feedback files has already been committed and pushed to the student repo
# then we can commit with a 'git commit -a -m "..."' command.
# But we want to be sure we don't modify their files.
# To do this:
# - change the commit method in core-scripts/Action.py to use -a flag
# - change Batch_Hwk_00.py to not attempt a 'git add'


# So 
# 1. get scripts working on my solutions
# 2. push dummy empty feedback file to students repos
# 3. run scripts


