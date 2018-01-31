import sys, os, subprocess
import logging
import config
sys.path.append ('{0}/dependencies/sh/'.format(config.gitgrade_path))
from sh import mkdir, rm, git

import Test

# Action
# intended to represent different assessment actions such as
# - running tests to compute scores for use in grading
# - running tests to provide feedback to students about their progress
#   - this may be done before the assignment due date, perhaps using
#     the WebHookServer to run this action when a student pushes 
#     code to their repository on github.umn.edu
# - writing and experimenting tests when creating an assignment
#   a candidate solution

class Action:
    '''Abstract Action.'''
    def __init__(self, course):
        self.course = course

        # These are initialized by sub-classes of Action.
        # grading_dir is absolute path to location of cloned student repos
        self.grading_dir = None
        # the set of tests to be run
        self.tests = None
        self.hwk_num = None
        self.isAssessment = None
        self.rmRepo = None
        
        # These are initialized by `setup` below
        self.uiid = None
        self.repo_path = None

        # ToDo: what is this for?
        self.homework_nums = None

    # -- Initialization steps
    # ------------------------------
    # student and logger-specific information.  
    # This must be set before assessment can be done.
    def setup(self, uiid, homework_nums=None):
        self.uiid = uiid

        self.repo_path = self.grading_dir + "/repo-" + uiid
        if not homework_nums:
            self.homework_nums = self.course.active_ass_nums
        else:
            self.homework_nums=homework_nums

        if not os.path.isdir(self.grading_dir):
            mkdir(self.grading_dir)
        os.chdir(self.grading_dir)

    # -- Git commands
    # ------------------------------
    def clone(self):
        cloneurl = "{0}:{1}/repo-{2}.git".format(self.course.github_ssh, self.course.github_org, self.uiid)

        try:
            if os.path.isdir("repo-{0}".format(self.uiid) ):
                rm("-Rf", "repo-{0}".format(self.uiid) )
        except:
            logging.error ( "Possibly removing existing repository {0}".format(self.uiid))

        logging.info("Cloning {0}".format(self.uiid))

        try:
            logging.info ("URL to clone {0}".format(cloneurl))
            git("clone", cloneurl)
            return True
        except:
            logging.error("Exception cloning {0}".format(cloneurl))
            logging.error("Unexpected Error{0}".format(sys.exc_info()))
            return False

    def cd_repo_path(self):
        '''Commit changes to repo.'''
        success=True
        try:
            os.chdir(self.repo_path)
            return success
        except:
            success=False
            logging.error("changing into directory {0} failed".format(self.repo_path))
            return success

    def commit(self):
        '''Commit changes to repo.'''

        if self.cd_repo_path():
            logging.info("Committing results to {0}".format(os.path.basename(self.repo_path)))
            # success = git("add", self.assessment_file)
            #try:
            #cmd = ["git", "commit", "-a", "-m", "GitBot results."]
            #p = subprocess.Popen(cmd)
            #p.wait()
            #res = p.poll()
            #out,err = p.communicate()
            #logging.info("Stdout of commit\n%s" % out)
            #logging.info("Stderr of commit\n%s" % err)
            try:
                git("commit", "-m", "GitBot results.")

            except:
                logging.warn("Commit failed, perhaps no staged changes to commit.")
                logging.error("Unexpected Error{0}".format(sys.exc_info()))
                pass
            os.chdir("../")
        else:
            logging.error("Committing to {0} failed".format(os.path.basename(self.repo_path)))
            logging.error("Unexpected Error{0}".format(sys.exc_info()))


    def push(self):
        '''Push commits to GitHub.'''
        if self.cd_repo_path():
            git("push")
        else:
            logging.error("Failed pushing results to {0}".format(os.path.basename(self.repo_path)))
            logging.error("Unexpected Error{0}".format(sys.exc_info()))

            
    #create a feedback file and add it to current commit
    def addResults(self, results):
        if isinstance(self.hwk_num, int):
            hwk_num = ("%02d" % (self.hwk_num,))
        else:
            hwk_num = self.hwk_num
        md = Test.showResults(results, self.isAssessment)
        try:
            os.chdir(self.repo_path)
            logging.info("Now in directory {0}".format(os.getcwd()))
            if self.isAssessment:
                feedback_file = "{0}/Hwk_{1}_Assessment.md".format(self.repo_path, hwk_num)
            else:
                feedback_file = "{0}/Hwk_{1}_Feedback.md".format(self.repo_path, hwk_num)
        except:
            logging.error("Could not change directory to {0}".format(self.repo_path))
            logging.error("Unexpected Error{0}".format(sys.exc_info()))
        resfile = open(feedback_file, "w")
        resfile.write(md)
        resfile.close()
        logging.info("Now in directory {0}".format(os.getcwd()))
        git("add", feedback_file)
        print("added {0}\n".format(feedback_file))

    # this function is broken, it cannot ever have been run
    # should be self.run_all and no self as first arg to run_all!
    def run_active(self, pushToGitHub):
        logging.info("Running all feedback or assessment for {0}'s active assignments".format(self.uiid))
        run_all(self, pushToGitHub, run_inactive=False)

    def run_all(self, pushToGitHub, run_inactive=True):
        self.clone_test_push(pushToGitHub, run_inactive=True)


    def clone_test_push(self, pushToGitHub, run_inactive=True):
        logging.info("Running all commands for feedback or assessment for {0}.".format(self.uiid))
        success=False
        try:
            os.chdir(self.grading_dir)
            success=True
        except:
            logging.error("Could not change into directory {0}. Skipping student {1}".format(grading_dir, self.uiid))
            logging.error("Unexpected Error{0}".format(sys.exc_info()))
            success=False

        if success:
            try:
                # Remove repo directory if it is there already
                self.cleanup()
                success = self.clone()
            except:
                logging.error("Failed to clone student {0} repo. Skipping student.".format(self.uiid))
                success = False
                logging.error("Unexpected Error{0}".format(sys.exc_info()))

        if success:
            try:
                os.chdir("repo-{0}".format(self.uiid))
            except:
                logging.error("Failed to change into directory repo-{0}".format(self.uiid))
                success=False
                logging.error("Unexpected Error {0}".format(sys.exc_info()))

        if success:
            if ( (run_inactive) or (self in self.course.feedbacks[a] for a in self.course.active_ass_nums) ):

                logging.info("Running Hwk_{0} tests".format(self.hwk_num))
                logging.info("... starting in directory {0}".format(os.getcwd()))
                # self.run_tests()  - don't do this anymore
                results = self.tests.run()
                Test.computeTotalScore(results)
                
                logging.info("Finished, now in directory {0}".format(os.getcwd()))

                self.addResults(results)

                csvString=Test.csvResults(results,self.uiid)
                csvFileName = "{0}/{1}_Hwk_{2}.csv".format(self.grading_dir, self.uiid, self.hwk_num)
                logging.info("Writing CSV grades file to {0}".format(csvFileName))
                csvfile = open(csvFileName, "w+")
                csvfile.write(csvString)
                csvfile.flush()


        if pushToGitHub:
            try:
                self.commit()
                self.push()
            except:
                logging.error("Failed to commit and push {0}".format(self.uiid))
                logging.error("Unexpected Error{0}".format(sys.exc_info()))

        if self.rmRepo:
            self.cleanup()

        # Once complete, return to grading directory.
        logging.info("Returning to grading directory: {0}"
                     .format(self.grading_dir))
        os.chdir(self.grading_dir)
                        
    def cleanup(self):
        logging.info("Cleaning up: removing {0}".format(self.repo_path))
        rm("-Rf", self.repo_path)

class Assessment(Action):
    '''Abstract Assessment.'''

    def __init__(self, course):
        Action.__init__(self, course)
        self.isAssessment = True

class Feedback(Action):
    '''Abstract Feedback.'''

    def __init__(self, course):
        Action.__init__(self, course)
        self.isAssessment = False

