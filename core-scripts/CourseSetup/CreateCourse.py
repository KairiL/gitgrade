import csv, re, shutil, sys, fileinput, os, subprocess
from getpass import getpass, getuser
import config
sys.path.append("{0}/dependencies/github3.py".format(config.gitgrade_path) )
sys.path.append("{0}/dependencies/uritemplate".format(config.gitgrade_path) )
sys.path.append("{0}/dependencies/sh".format(config.gitgrade_path) )
from sh import git, python3, rm
import github3
sys.path.append("{0}/core-scripts".format(config.gitgrade_path) )
import Util
new_course_input="new_course.csv"

attributes=['title', 'name', 'department', 'course_number', 'session', 'year', 'section', 'instr_uiids', 'TA_uiids', 'grad_uiids', 'ugrad_uiids', 'sample_uiids']
github='https://github.umn.edu'

def genSubFile(filename, reponame, to_replace, replace_with, missing_okay=False):
    """
    Takes in an template <filename> and copies it to <reponame> directory.
    All instances of <to_replace> are replaced with <replace_with>.
    if <missing_okay> is True missing files are skipped instead of exiting
    """

    f = None
    if os.path.isfile("templates/{0}".format(filename)):
        f = open("templates/{0}".format(filename),'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace(to_replace, replace_with)
        f = open("/".join([config.gitgrade_path, reponame, filename]),'w')
        f.write(newdata)
        f.close()
    elif not missing_okay:
        print("Error: source file {0} does not exist. Exiting.".format(filename) )
        sys.exit(1)
    else:
        print("Source file {0} does not exist. Continuing.".format(filename) )
        return

    
def genCourseFile(course_desc, dest_dir):
    """
    Generates main course file using <course_desc> template inside <dest_dir> directory
    """
    course_file = course_desc.name
    course_file = re.sub(r'\W+', '', course_file)+ '.py'

    course_def_line="class {0}(Course):\n".format(re.sub('-','', course_desc.name))
    course_pre_init_lines='''    """
    This is the base class for your course
    """
    def __init__(self):
'''
    course_tail_lines='''
if __name__ == "__main__":
    thisClass = {0}()
    thisClass.initialize_team_repos()

'''.format(re.sub('-','', course_desc.name))
    new_file="{0}/{1}/{2}".format(config.gitgrade_path, dest_dir, course_file)
    if not os.path.exists("{0}/{1}".format(config.gitgrade_path, dest_dir) ):
        print("Destination directory {0}/{1} does not exist\n".format(config.gitgrade_path, dest_dir) )
        print("Exiting.")
        sys.exit(1)

    with open("./templates/course_template.py", 'r') as fr,open(new_file, 'w') as fw:
        for line in fr:
            if (line.find("COURSE_DESCRIPTION_HEAD")==-1):
                if (line.find("#TODO")==-1):
                    fw.write(line)
            else:
                fw.write(course_def_line)
                fw.write(course_pre_init_lines)
                for attr in attributes:
                    fw.write("        ")
                    if (isinstance(getattr(course_desc,attr), str)):
                        fw.write("self.{0} = '{1}'\n".format(attr, getattr(course_desc,attr) ) )
                    else:
                        fw.write("self.{0} = {1}\n".format(attr, getattr(course_desc,attr) ) )
        fw.write(course_tail_lines)
        fw.truncate()

def genGradingRepo(course_desc, user, password):
    # Login to github enterprise.

    gh = None
    try:
        enterprise = github3.GitHubEnterprise(github, user, password=password)
        stats = enterprise.admin_stats("all")
        gh = enterprise
    except:
        gh = None
        print("Could not connect or login to server.\n");
        sys.exit(1)

    success=False
    # Enter organization
    organization = new_desc.name
    org=None

    try:
        print("Accessing organization: {0}\n".format(organization))
        org = gh.organization(organization)
    except:
        print("Problem accessing organization {0}:\n".format(organization))
        sys.exit(1)

    if not org:
        print("Organization {0} does not exist or you do not have access rights\n".format(organization))
        print('Create a new organization named "{0}".\n'.format(organization))
        print('Add robot006 as an owner of the organization.')
        print("Then re-run course creation script\n")
        print('''WARNING: Go to "Settings"->"Member Privileges" and \nchange "Default repository permission" to "None"!\n''')
        sys.exit(1)
    repo = None
    repoadded = False
    success = False
    reponame = "-".join([course_desc.name, "grading-scripts"])
    for r in org.repositories():
        if r.name == reponame:
            print("Repo \"{0}\" already exists\n".format(reponame))
            repo = r
            success = True
            repoadded = False
    if repo is None:
        try:
            print("Creating repo {0}\n".format(reponame))
            repo = org.create_repository(reponame,
                                   description='',
                                   homepage='',
                                   private=True,
                                   has_issues=True,
                                   has_wiki=True,
                                   auto_init=True,
            )
            repoadded = True
            success=True
        except:
            print("Failed to create repo {0}:\n".format(reponame))
            repo = None

    if not repoadded:
        if not success:
            print("Could not create or access repo. Exiting from {0}".format(__file__))
            sys.exit(1)
        else:
            print("Repo already exists. Continuing.\n")
    ## Add TAs and instructors as collaborators to grading script repo
    for instr in new_desc.instr_uiids:
        repo.add_collaborator(instr)
    for TA in new_desc.TA_uiids:
        repo.add_collaborator(TA)

def genGradingDir(reponame):
    try:
        if not os.path.exists("{0}/{1}/grading".format(config.gitgrade_path, reponame) ):
            os.makedirs("{0}/{1}/grading".format(config.gitgrade_path, reponame) )
        else:
            print("Grading script directory already exists.  Continuing.\n")
    except:
        print("Failed to create grading directory in grading scripts directory\n")
    try:
        os.utime("{0}/{1}/grading/README.md".format(config.gitgrade_path, reponame), None )
    except:
        open("{0}/{1}/grading/README.md".format(config.gitgrade_path, reponame), 'a').close()

class CourseDescription:
    """
    Course description used for generating the new course file
    """
    def __init__(self):
        self.title=""
        self.department=""
        self.course_number=0
        self.session=""
        self.year=0
        self.section=""
        self.instr_uiids=[]
        self.TA_uiids=[]
        self.grad_uiids=[]
        self.ugrad_uiids=[]
        self.sample_uiids=[]
        with open(new_course_input, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if (len(row)>1):
                    setattr(self, row[0], row[1:])
                elif (getattr(self, row[0])==None):
                    print ("Required field missing: {0}\n".format(row[0]))
                    print ("Exiting.\n")
                    sys.exit(1)
        
        #reformat and clean input from csv file
        self.title=str(self.title[0])
        self.department=str(self.department[0])
        self.course_number=int(self.course_number[0])
        self.session=str(self.session[0])
        self.year=int(self.year[0])
        self.section=str(self.section[0])
        self.instr_uiids=[x for x in self.instr_uiids if x]
        self.TA_uiids=[x for x in self.TA_uiids if x]
        self.grad_uiids=[x for x in self.grad_uiids if x]
        self.ugrad_uiids=[x for x in self.ugrad_uiids if x]
        self.sample_uiids=[x for x in self.sample_uiids if x]
        self.name = "{0}{1}{2}{3}".format(self.department, self.course_number, self.session, self.year)
        if self.section:
            self.name+="{0}".format(self.section)

new_desc = CourseDescription()
if not new_desc.name.isalnum():
    print ("Invalid use of non-alphanumeric character.  Please use only alphanumeric characters. Exiting\n")
    sys.exit(1)

#get login and password for github
#first attempts to use git config user. If that fails, use local username
try:
    user = git("config", "user.login")
except:
    try:
        user=getuser()
        print("used local user: {0}\n".format(user))
    except:
        print('could not retrieve username')
        sys.exit(1)

password = ''
while not password:
    password = getpass('Password for {0}: '.format(user))

genGradingRepo(new_desc, user, password)

reponame = "-".join([new_desc.name, "grading-scripts"])
git_repo="ssh://git@github.umn.edu/{0}/{1}.git".format(new_desc.name, reponame)

clone_scripts=False
if os.path.exists("{0}/{1}".format(config.gitgrade_path, reponame)):
    print("Course script directory already exists.")
    if Util.queryYesNo("Would you like to replace the existing course script directory?"):
        rm("-rf", "{0}/{1}".format(config.gitgrade_path, reponame))
        clone_scripts=True
else:
    clone_scripts=True

if clone_scripts:
    try:
        git('clone', git_repo, _cwd=config.gitgrade_path)
    except:
        print("You lack permission to clone. Exiting\n")
        sys.exit(1)
#Finished create course script repository.
####################

# Add example tests and course file to local course directory
genCourseFile(new_desc, reponame)
try:
    git('add', "{0}.py".format(new_desc.name), _cwd="/".join([config.gitgrade_path, reponame]) )
except:
    print("Failed to add local course directory files to repo\n")
    sys.exit(1)

file_list=["Batch_Hwk_00.py", "README.md", "Feedback_Hwk_00.py", "Hwk_00_Tests.py", "Go.py", "config.py", "config.examp", ".gitignore"]
for f in file_list:
    genSubFile(f, reponame, "TestClass", new_desc.name)
    if (f != "config.py"):
        try:
            git('add', f, _cwd="/".join([config.gitgrade_path, reponame]) )
        except:
            print("Failed to add local course directory files to repo\n")
            print("Exiting.\n")
            sys.exit(1)

genGradingDir(reponame)
try:
    git('add', "grading/", _cwd="/".join([config.gitgrade_path, reponame]) ) 
except:
    print("failed to add local grading directory to repo\n")
    print("Exiting.\n")
    sys.exit(1)
    

try:
    git('commit', '-m', '"grading script initialization"', _cwd="/".join([config.gitgrade_path, reponame]))
except:
    print("Failed grading script initial commit. Possibly no changes to commit\n")

# Push all files created in local course directory
try:
    git('push', _cwd="/".join([config.gitgrade_path, reponame]))
except:
    print("Failed grading script initial push.  Possibly no changes to push\n")

os.chdir("/".join([config.gitgrade_path, reponame]))
os.system("python3 {0}.py".format(new_desc.name))
