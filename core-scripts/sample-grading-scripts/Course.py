import sys, os, signal, getpass, logging
import config
sys.path.append ("{0}/core-scripts/".format(config.gitgrade_path) )
sys.path.append ("{0}/core-scripts/CourseSetup".format(config.gitgrade_path) )

from Action import Action
sys.path.append ("{0}/dependencies".format(config.gitgrade_path))
from sh import git, mkdir
from defaultoptions import getDefaultOptions


DEBUGGING = False

class course:
    """
    This class holds various setting for the course
    """
    #Full title of your course
    title = 'Rl 101: Paid Suffering'
    #Abbreviated name of your course
    name = 'rl-101F16'
    
    #x500s of course instructor(s)
    instr_uiids = ['cse-lassa005'] ##Change me!##
    #x500s of course TA(s)
    TA_uiids = [] ##Change me!##
    #x500s of graduate students
    grad_uiids = [] ##Change me!##
    #x500s of undergraduate students
    ugrad_uiids = ['lassa005'] ##Change me!##
    #fake x500s for script testing
    sample_uiids = ['user000', 'user050', 'user100', 'user0100']
    
    real_uiids = instr_uiids + TA_uiids+ grad_uiids+ ugrad_uiids
    all_uiids = real_uiids+ sample_uiids
    student_uiids = grad_uiids+ ugrad_uiids
    
    # Directories used by GitBot to grade assignments.
    # If directories are not unique per gitbot you risk overwriting
    # another directory
    grading_home_dir = "{0}/grading-scripts/grading".format(config.gitgrade_path)
    logging_home_dir = "{0}/grading-scripts/logging".format(config.gitgrade_path)

    #github organization name used for all class members e.g.: "umn-rl-101F16"
    github_org = "umn-rl-101F16" ##Change me to match your github organization name!##

    #ssh prefix based on github enterprise address
    github_ssh = "git@github.umn.edu"
    
    #html prefix based on github enterprise address
    github_https = 'https://github.umn.edu'

    #public class repo; should contain course and homework instructions
    pub_repo="public-class-repo.git" 

    #list of homework assignment numbers that are open to students
    active_ass_nums=["00"] ##Change me whenever you add or remove an assignment!

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
        """
        Initializes local directory for grading if it doesn't already exist
        """
        try:
            os.chdir(config.gitgrade_path)
            if not os.path.isdir(self.grading_home_dir):
                mkdir("-p", self.grading_home_dir)
        except:
            logging.critical("Error initializing grading directory in {0}\n".format(__file__) )

    def initialize_team_repos(self):##Depricated.  Replaced by UpdateStudentRepos.py
        """
        Initializes team github repos for all users in self.all_uiids.
        If a team or repo already exists, it attempts to complete 
        initialization.
        """
        ghlogin=getpass.getuser()
        os.system("../core-scripts/CourseSetup/CreateTeamRepoPerUId.py -u "+ ghlogin+ " --org "+ self.github_org+ " "+ " ".join(self.all_uiids))

    def pull_repo(self, repo):
        try:
            git("pull", self.github_ssh+ ":"+ self.github_org+ "/"+ repo)
        except :
            logging.error("Timeout pulling.  You may need to create an ssh key for gitbot account and github\n")
            logging.error("for more info go to https://help.github.com/articles/generating-an-ssh-key/\n")
            logging.error("Unexpected Error{0}\n".format(sys.exc_info()))

if sys.version_info <= (3, 0):
    sys.stdout.write("Sorry, requires Python 3.0+\n")
    sys.exit(1)


