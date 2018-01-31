import os, logging, datetime, sys, subprocess, csv
import config
sys.path.append('{0}/dependencies/sh'.format(config.gitgrade_path) )
from sh import git, cat, echo
sys.path.append ('{0}/core-scripts/'.format(config.gitgrade_path) )
import Test
import Action

from TestClass import TestClass

import Hwk_00_Tests

class Hwk_00_Feedback(Action.Feedback):
    '''Feedback for Hwk 00 in RL 102'''

    def __init__(self):
        Action.Feedback.__init__(self, TestClass())

        # Define course tests for this feedback.
        # --------------------------------------------------
        current_date = datetime.datetime.now()
        self.timestamp = current_date.strftime("%B %d, %H:%M:%S %p")
        print ("Timestamp: {0}\n\n".format(self.timestamp))

        all_tests = Test.SequenceTest ([ 
                       Test.Message("### Feedback for Homework 0"),
                       Test.TimestampMessage(),
                       Test.FailingSequenceTest ([ 
                         Hwk_00_Tests.dir_exists, 
                         Hwk_00_Tests.file_exists,

                       ]) 
        ])
        """
        some_tests = Test.SequenceTest ([ 
                       Test.Message("### Assessment for Homework 0"),
                       Test.TimestampMessage(),
                       Test.FailingSequenceTest ([ 
                         Hwk_00_Tests.dir_exists, 
                         Hwk_00_Tests.file_exists,

                       ]) 
        ])
        """
        self.tests = all_tests

    def run_tests(self):
        current_date = datetime.datetime.now()
        timestamp = current_date.strftime("%B %d, %H:%M:%S %p")

        print ("Timestamp: %s\n\n" % timestamp)

        self.clone()
        os.chdir(self.repo_path)
        for n in self.homework_nums:
            logging.info("Running Hwk_{0} tests".format(n))
            logging.info("... starting in directory {0}".format(os.getcwd()))

            results = self.tests.run()
            logging.info("Finished, now in directory {0}".format(os.getcwd()))
            
            self.addResults(results, n, isAssessment=False)
            
            logging.info("Now in directory {0}".format(os.getcwd()))
            
            # maybe put all of these in a "csv" directory
            csvdata = Test.csvResults(results, self.uiid)
            csvfile = open("{0}/{1}_Hwk_{2}.csv".format(self.grading_dir, self.uiid, n), "w+")
            print (csvdata, file=csvfile)
            csvfile.flush()
            
            
            # Read all data from the csv file.
            result_list=[]
            if os.path.isfile("{0}/Hwk_{1}.csv".format(self.grading_dir, n)):
                with open("{0}/Hwk_{1}.csv".format(self.grading_dir, n), "r") as b:
                    for row in csv.reader(b, delimiter=' ', quoting=csv.QUOTE_MINIMAL):
                        result_list.extend(row)
                    
            with open("{0}/Hwk_{1}.csv".format(self.grading_dir, n), "w") as b:
                writer = csv.writer(b, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
                appendcsv=True
                for row in result_list:
                    if self.uiid in row:
                        writer.writerow([csvdata])
                        appendcsv=False
                    else:
                        writer.writerow([row])
                if appendcsv:
                    writer.writerow([csvdata])
        self.commit()
        self.push()
        self.cleanup()        
            #TODO: also print this data to collective class scores csv file
        
        #Test.csvResults(results, self.uiid)

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


