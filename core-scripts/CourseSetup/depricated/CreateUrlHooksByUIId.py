#!/usr/bin/python3

# This script allows repos owned by teams and matching certain filters to create web hooks
# Example call:
#  python3 CreateUrlHooksByUIId.py --user dacos014 --github https://github.umn.edu 
#     --org csci2041-f15 --url http://www.google.com/ user0001 user0002 user0003
#
# This causes a webhook hook pointing to http://www.google.com/ to be installed on a 
# repositories named "repo-user0001", "repo-user0002", and "repo-user0003". 
#
# NOTE: An empty url will remove all web hooks attached to the following teams


# System level imports.
from defaultoptions import getDefaultOptions
import os
import sys
import inspect
import argparse
import traceback
import re
from getpass import getuser, getpass
import config
# Add additional dependencies relative to the real location of this file.
sys.path.insert(0, "{0}/dependencies/github3.py".format(config.gitgrade_path))
sys.path.insert(0, "{0}/dependencies/requests".format(config.gitgrade_path))
sys.path.insert(0, "{0}/dependencies/uritemplate".format(config.gitgrade_path))
sys.path.insert(0, "{0}/dependencies/sh".format(config.gitgrade_path))

# Path relative imports.
import github3
import logger

def __checkRegExp(regexp):
    try:
        return re.compile(regexp)
    except re.error:
        msg = "Invalid regular expression"
        raise argparse.ArgumentTypeError(msg)

# Setup command line argument parser.
argparser = getDefaultOptions("Modify repos belonging teams associated with uids.",user=True)
argparser.add_argument("uid",metavar="uid", help="Student id.",nargs="+",type=str)
argparser.add_argument("--url",help="This is used to specify the url of the web hooks you want applied to the repos",default='',type=str)
teamformathelpstr = """A format string indicating how the team name relates to the uid. An example string would be 'team-{uid}."""
argparser.add_argument("--teamformat", help=teamformathelpstr,default="team-{uid}", dest='teamformat', type=str)
argparser.add_argument("--repofilter", help='A regular expression to filter repositories names by.', default=".*", type=__checkRegExp)
argparser.add_argument("--remove", help='Remove all hooks attached to repositories', default=False, type=bool)
# Parse command line arguments.
args = argparser.parse_args()

# Setup logger.
logger = logger.getLogger(args.loglevel,args.logfile)

# Get credentials
password = None
while not password:
    password = getpass('Password for {0}: '.format(args.user))

# Login to github enterprise.
gh = None
try:
    enterprise = github3.GitHubEnterprise(args.github
                                          , username=args.user
                                          , password=password)
    gh = enterprise
    gh.zen()
except:
    gh = None
    logger.critical("Failed to login as user %s:\n%s" % (args.user,traceback.format_exc()))
    print("Could not connect or login to server.");
    sys.exit(1)

# Enter organization.
try:
    org = gh.organization(args.org)
except:
    logger.critical("Problem accessing organization %s:\n%s" % (args.org,traceback.format_exc()))
    print("Could not access organization %s." % args.org)
    sys.exit(1)

# Process uids.
for uid in args.uid:

    logger.info("Processing %s." % uid)

    # Build team names from format string and uid.
    interpolationvalues = { 'uid' : uid }
    teamname = args.teamformat.format(**interpolationvalues)

    # Find the team associated with this uid.
    team = None
    success = False
    for t in org.teams():
        if t.name == teamname and team == None:
            team = t
            logger.info("Found team %s for uid %s." % (teamname,uid))
            success = True
                
    if not success:
        msg = "Could not find team, ignoring uid %s." % uid
        logger.error(msg)
        print(msg)        
        continue
        

    # Loop through the team repos.
    hook_created = False
    for repo in team.repositories():
        # Skip this repo if it does not match the filter.
        if not args.repofilter.match(repo.name): 
            continue

        # Check to see if URL is valid
            # Maybe some ping fuction 


        # Change the hooks
        try:
            for hook in repo.hooks():
                hook.delete()
            repo.create_hook(name="web",config={"url":args.url, "content_type":"json"}) if args.url else None
        except:
            logger.error("Failure while setting hook for %s:\n%s"%(repo.name,traceback.format_exc()))
            logger.error("URL hook that failed: %s"%args.url)
            print("Ignoring %s; a failure was encountered during modification."%repo.name)


