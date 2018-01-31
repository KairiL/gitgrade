import sys
import os
import logging
import datetime
import config
sys.path.append ('{0}/dependencies/sh/'.format(config.gitgrade_path) )
from sh import mkdir, rm, git

class BatchRun:
    '''Class for batch running of feedback or grading scripts.'''
    def __init__(self, course, action):
        self.course = course
        self.action = action
        self.grading_dir_name = action.grading_dir

    def run(self, uiids, pushToGitHub):
        # Delete and then recreate grading directory
        # --------------------------------------------------
        #grading_dir = os.path.abspath(self.course.grading_home_dir) + "/" + self.grading_dir_name

        self.course.initialize_grading_dir()

        # Set up the logger
        # ------------------------------
        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%m_%d_%H_%M_%S")

        log_filename = self.course.logging_home_dir + "/log.log"
        if not os.path.exists(self.course.logging_home_dir):
            os.makedirs(self.course.logging_home_dir)

        print ("log file name: %s" % log_filename)
        logger = logging.getLogger(log_filename) # TODO: call logger.getLogger instead?  
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            filemode='w',
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M')


        logging.info("+++++++++++++++++++++++++++++++++++++++++")
        logging.info("+++++++++++++++++++++++++++++++++++++++++")

        for uiid in uiids:
            logging.info("--------------------------------------------------")
            logging.info("Working on %s" % uiid)
            logging.info("-------------------")
            self.action.setup(uiid)
            self.action.clone_test_push(pushToGitHub)


    def run_samples(self, pushToGitHub):
        '''Run the action in batch mode on the sample uiids'''
        self.run(self.course.sample_uiids, pushToGitHub)

    def run_few(self, pushToGitHub):
        '''Run the action in batch mode on the just a few real course uiids'''
        self.run(self.course.few_uiids, pushToGitHub)

    def run_all(self, pushToGitHub):
        '''Run the action in batch mode on all of the real course uiids'''
        self.run(self.course.all_uiids, pushToGitHub)

    def run_specific(self, uiids, pushToGitHub):
        '''Run the action in batch mode on specific names uiids'''
        self.run(uiids, pushToGitHub)


