import sys, os, signal, getpass, logging
import config
sys.path.append ("{0}/core-scripts/".format(config.gitgrade_path))
sys.path.append ("{0}/core-scripts/CourseSetup".format(config.gitgrade_path))

from Course import Course
from Action import Action
sys.path.append ("{0}/dependencies".format(config.gitgrade_path))
from sh import git
from defaultoptions import getDefaultOptions

DEBUGGING = False

COURSE_DESCRIPTION_HEAD #code here will be generated from user input

        self.real_uiids = self.instr_uiids+ self.TA_uiids+ self.grad_uiids+ self.ugrad_uiids
        self.all_uiids = self.real_uiids+ self.sample_uiids
        
        #Directories used by GitBot to grade assignments
        #If directories are not unique per gitbot you risk overwriting another directory
        self.grading_home_dir = "{0}/{1}-grading-scripts".format(config.gitgrade_path,self.name)
        self.logging_home_dir = self.grading_home_dir

        #github organization name used for all class members e.g.: "rl101F16"
        self.github_org = self.name

        self.github_ssh = "git@github.umn.edu" #ssh prefix based on github enterprise address
        self.github_https = 'https://github.umn.edu'#html prefix based on github enterprise address
        self.pub_repo="public-class-repo.git" #public class repo; should contain course and homework instructions        
        
        self.active_ass_nums=[0] #list of homework assignment numbers that are open to students

    def initialize_pub_dir(self):
        """
        Initializes the public class repo for instructions, syllabus, etc.
        """
        try:
            git("clone", self.github_ssh+ ":"+ self.github_org+ "/"+ self.pub_repo)
        except:
            logging.error("Error cloning.\n")
            logging.error("Unexpected Error{0}\n".format(sys.exc_info()))
            logging.error("Continuing...\n")

    def initialize_grading_dir(self):
        #currently done by CreateCourse.py
        """
        Initializes local grading scripts directory from GitHub repo
        """
        try:
            os.chdir(config.gitgrade_path)
            rm("-Rf", self.grading_home_dir)
            mkdir("-p", self.grading_home_dir)
            os.chdir(self.grading_home_dir)
            git("clone", self.github_ssh+ ":"+ self.github_org+ "/"+ self.grading_home_dir)
        except:
            logging.error("Error initializing grading directory in __file__\n")
            logging.error("You may need to create an ssh key or delete existing grading directory\n")
            logging.error("Continuing\n")

    def initialize_team_repos(self):
        """
        Initializes team github repos for all users in self.all_uiids
        If a team or repo already exists, it attempts to complete initialization
        """
        ghlogin=getpass.getuser()
        os.system("../core-scripts/CourseSetup/CreateTeamRepoPerUId.py -u "+ ghlogin+ " --org "+ self.github_org+ " "+ " ".join(self.all_uiids))

    def pull_repo(self, repo):
        try:
            git("pull", self.github_ssh+ ":"+ self.github_org+ "/"+ repo)
        except :
            #TODO specific exceptions
            logging.error("Timeout pulling.  You may need to create an ssh key for gitbot account and github\n")
            logging.error("for more info go to https://help.github.com/articles/generating-an-ssh-key/\n")
            logging.error("Unexpected Error{0}\n".format(sys.exc_info()))

if sys.version_info <= (3, 0):
    sys.stdout.write("Sorry, requires Python 3.0+\n")
    sys.exit(1)
