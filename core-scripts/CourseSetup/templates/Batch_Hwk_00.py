import os
import logging
import datetime
import sys, subprocess
import config
sys.path.append('{0}/dependencies/sh'.format(config.gitgrade_path) )
from sh import git, cat, echo

sys.path.append ('{0}/core-scripts/'.format(config.gitgrade_path) )
from Batch import BatchRun
import Test
from Action import Feedback

from TestClass import TestClass

import Hwk_00_Tests

class Hwk_00_Feedback(Feedback):
    '''Assessment for Hwk 00 in RL 101'''

    def __init__(self):
        Feedback.__init__(self, TestClass() )

        # Define course tests for this feedback.
        # --------------------------------------------------
        current_date = datetime.datetime.now()
        self.timestamp = current_date.strftime("%B %d, %H:%M:%S %p")
        print ("Timestamp: {0}\n\n".format(self.timestamp) )

        all_tests = Test.SequenceTest ([ 
                       Test.Message("### Assessment for Homework 0"),
                       Test.TimestampMessage(),
                       Test.FailingSequenceTest ([ 
                         Hwk_00_Tests.dir_exists, 
                         Hwk_00_Tests.file_exists                         

                       ]) 
        ])

        self.tests = all_tests

    def run_tests(self):
        current_date = datetime.datetime.now()
        timestamp = current_date.strftime("%B %d, %H:%M:%S %p")

        print ("Timestamp: {0}\n\n".format(timestamp) )

        logging.info("Running rl 101 Hwk_00 tests")
        logging.info("... starting in directory {0}".format(os.getcwd() ) )

        results = self.tests.run()
        logging.info("Finished, now in directory {0}".format(os.getcwd() ) )

        md = Test.showResults(results, forFeedback=True)

        os.chdir(self.repo_path)
        logging.info("Now in directory {0}".format(os.getcwd() ) )

        feedback_file = "{0}/Hwk_00_Feedback.md".format(self.repo_path)
        resfile = open(feedback_file, "w")
        print (md, file=resfile)
        resfile.flush()

        logging.info("Now in directory {0}".format(os.getcwd() ) )

        git("status")
        git("add", feedback_file)

        logging.info("Now in directory {0}".format(os.getcwd() ) )

        # maybe put all of these in a "csv" directory
        csvdata = Test.csvResults(results, self.uiid)
        csvfile = open("{0}/{1}.csv".format(self.grading_dir, self.uiid), "w+")
        print (csvdata, file=csvfile)
        csvfile.flush()



