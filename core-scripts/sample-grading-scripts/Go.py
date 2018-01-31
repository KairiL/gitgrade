import sys, os, re, getopt, argparse, logging, json, ast
import config

import Course

import Hwk_00_Feedback ##Change me when adding or removing active assignments!

# This import seems to fail.  Not sure why.
import WebHookUtil

feedbacks={ ##Change me when adding or removing active assignments!
    "00": Hwk_00_Feedback.Hwk_00_Feedback,
    "0": Hwk_00_Feedback.Hwk_00_Feedback,
    0: Hwk_00_Feedback.Hwk_00_Feedback,
}

# Configure the command line interface.
parser = argparse.ArgumentParser(
'''Go Goes.''')
parser.add_argument("hdrs", help="headers from github webhook")
parser.add_argument("json",help="JSON content from github webhook.")
parser.add_argument("log_file", help="name of the file for log output from Go.py:")
args = parser.parse_args()
DEBUG=True


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# Initialize pythons logging facilities.
logging.basicConfig(
    filename="{0}/{1}.log".format(Course.course.logging_home_dir,args.log_file),
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M')

# Returns the course name that assignment was pushed for
def getCourse(hdrs,payload):
    func_name="getCourse"
    logging.info("entered {0}".format(func_name))
    if hdrs['X-GitHub-Event'] == 'push':
        logging.info("getCourse found course {0}".format(payload['repository']['owner']['name']))
        return payload['repository']['owner']['name']
    else:
        return None

# Returns a list of homework assignment numbers that have changed
def getAssignNums(commits):
    func_name="getAssignNums"
    logging.info("entered {0}".format(func_name))
    strings=[s for s in getEditedFiles(commits) if 'Hwk_' in s]
    logging.info("edited files in getAssignNums: {0}\n".format(strings))
    hwNums=[s.split('Hwk_')[1][:2] for s in strings]
    numSet=set()
    for n in hwNums:
        if isInt(n):
            numSet.add(int(n))
    return list(numSet)

# NB: Some events do not have an appropriate email address readily
# available.
def getEmailAddr(hdrs,payload):
    func_name="getEmailAddr"
    logging.info("entered {0}".format(func_name))
    if hdrs['X-GitHub-Event'] == 'push':
        return payload['head_commit']['author']['email']
    else:
        return None

# Returns a list of files that have been edited in the last push
def getEditedFiles(commits):
    func_name="getEditedFiles"
    logging.info("entered {0}".format(func_name))
    edited_files = []
    for commit in commits:
        edited_files += (commit['modified'])
        edited_files += (commit['added'])
        edited_files += (commit['removed'])
    return edited_files

def checkCommitMsgs(commits):
    func_name="checkCommitMsgs"
    logging.info("entered {0}".format(func_name))
    runTest = True
    for commit in commits:
        msg = (commit['message'])
        logging.info("Commit msg: {0}".format(msg))
        if "GitBot" in msg:
            logging.info("DON'T RUN IT.")
            runTest = False
    return runTest

def getRepoUrl(hdrs, payload):
    func_name="getRepoUrl"
    logging.info("entered {0}".format(func_name))
    if hdrs['X-GitHub-Event'] == 'push':
        return payload['repository']['url']
    else:
        return None

def getRepoName(payload):
    func_name="getRepoName"
    logging.info("entered {0}".format(func_name))
    return payload['repository']['name']

#pushTicket contains "course_name","edited_files","repo_name","uiid","ass_nums","run_tests","email","repo_url"
def go(hdrs, payload, course):
    """
    Main driver function called by the webhook server for live feedback
    """
    course.initialize_grading_dir()
    
    func_name="go"
    logging.info("entered {0}".format(func_name))
    commits=payload['commits']
    pushTicket = {
                "hdrs": hdrs,
                "payload": payload,
                "course_name": getCourse(hdrs,payload),
                "edited_files": getEditedFiles(commits),
                "repo_name": getRepoName(payload),
                "uiid": re.sub('repo-', '', getRepoName(payload)),
                "assign_nums": getAssignNums(commits),
                "run_tests": checkCommitMsgs(commits),
                "email": getEmailAddr(hdrs,payload),
                "repo_url": getRepoUrl(hdrs,payload),
    }
    if pushTicket["run_tests"]:
        logging.info("running tests\n")
        for n in pushTicket["assign_nums"]:
            logging.info("test for hwk_{0}\n".format(n))
            fb=feedbacks[n]()
            fb.setup(uiid=pushTicket["uiid"],
                    homework_nums=[n]
            )
            fb.clone_test_push(True)
            #fb.run_tests()
            
logging.info("Entered Go.py")
logging.info("Header:\n{0}\n".format(args.hdrs))
logging.info("payload:\n{0}\n".format(args.json))
#headers=json.loads(args.hdrs)
#payload=json.loads(args.json)
go(ast.literal_eval(args.hdrs), ast.literal_eval(args.json), Course.course())
