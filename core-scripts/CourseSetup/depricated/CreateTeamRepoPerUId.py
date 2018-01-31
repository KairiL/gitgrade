#!/usr/bin/python3

# System level imports.
from defaultoptions import getDefaultOptions
import os, sys, inspect, argparse, traceback
from getpass import getuser, getpass
import logger

# Add additional dependencies relative to the real location of this file.
import config
sys.path.append("{0}/dependencies/github3.py".format(config.gitgrade_path))
sys.path.append("{0}/dependencies/requests".format(config.gitgrade_path))
sys.path.append("{0}/dependencies/uritemplate".format(config.gitgrade_path))
sys.path.append("{0}/dependencies/sh".format(config.gitgrade_path))
#plumbum installed on cs machines

# Path relative imports.
import github3

# Setup command line argument parser.
argparser = getDefaultOptions("Create a new team containing a student id and add a newly created repo to that team.",user=True)
teamformathelpstr = """A format string indicating how the team name should be created based on the uid. An example string would be 'team-{uid}."""
argparser.add_argument("--teamformat", help=teamformathelpstr,default="team-{uid}", dest='teamformat', type=str)
repoformathelpstr = """A format string indicating how the repo name should be created based on the uid. An example string would be 'repo-{uid}."""
argparser.add_argument("-repoformat", help=repoformathelpstr, default="repo-{uid}", dest='repoformat', type=str)
argparser.add_argument("uid",metavar="uid", help="Student id.",nargs="+",type=str)

# Parse command line arguments.
args = argparser.parse_args()

# Setup logger.
logger = logger.getLogger(args.loglevel,args.logfile)

# Get credentials
password = ''
while not password:
    password = getpass('Password for {0}: '.format(args.user) )

# Login to github enterprise.
gh = None
try:
    print("User {0}\n".format(args.user) )
    print("args.github={0}".format(args.github) )
    enterprise = github3.GitHubEnterprise(args.github,args.user,password=password)
    stats = enterprise.admin_stats("all")
    gh = enterprise
except:
    gh = None
    logger.critical("Failed to login as user {0}:\n{1}".format(args.user,traceback.format_exc() ) )
    print("Could not connect or login to server.")
    sys.exit(1)

# Enter organization.
try:
    org = gh.organization(args.org)
except:
    logger.critical("Problem accessing organization {0}:\n{1}".format(args.org,traceback.format_exc() ) )
    print("Could not access organization {0}.".format(args.org) )
    sys.exit(1)


# Process uids.
for uid in args.uid:

    logger.info("Starting setup for {0}.".format(uid) )
    
    # Build team and repo names from format string and uid.
    interpolationvalues = { 'uid' : uid }
    teamname = args.teamformat.format(**interpolationvalues)
    reponame = args.repoformat.format(**interpolationvalues)

    # Create team.
    team = None
    teamadded = False
    success = False

    for t in org.teams():
        if t.name == teamname:
            logger.info("Team \"{0}\" already exists".format(teamname) )
            team = t
            success = True
            teamadded = False

    if team is None:
        try:
            logger.info("No {0} team found, creating one.".format(teamname) )
            team = org.create_team(teamname,[],"push")
            teamadded = True
            success = True
        except:
            team = None
            logger.error("Failed during team creation process for team {0}:\n{1}".format(teamname,traceback.format_exc() ) )

    if not success:
        print("Failed to create team {0}, ignore setup for {1}".format(teamname,uid) )
     
    # Add uid to team. If this fails remove the team and continue.
    success = False    
    try:
        logger.info("Attempting to add {0} to team {1}.".format(uid,teamname) )
        
        if team.is_member(uid):
            logger.warning("Uid {0} is already a part of team {1}.".format(uid,teamname) )
            success=True
        else:
            logger.info("Adding {0}.".format(uid) )
            team.invite(uid)
            success = True
    except:
        logger.error("Failed to add {0} to team {1}:\n{2}".format(uid,teamname,traceback.format_exc() ) )
        success = False

    if not success:
        print("Failed to find {0}, deleting team {1} and ignoring setup for this user.".format(uid,teamname) )
        if teamadded:
            logger.debug("Removing team {0}.".format(teamname) )
            team.delete()
        continue

    # Create repository.
    repo = None
    repoadded = False
    success = False

    for r in org.repositories():
        if r.name == reponame:
            logger.info("Repo \"{0}\" already exists".format(reponame) )
            repo = r
            success = True
            repoadded = False
    if repo is None:
        try:
            logger.info("Creating repo {0}".format(reponame) )
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
            logger.error("Failed to create repo {0}:\n{1}".format(reponame,traceback.format_exc() ) )
            repo = None

    if not success:
        print("Failed to create repo {0}, deleting team and ignoring setup for {1}".format(uid ,reponame) )
        if teamadded:
            logger.debug("Removing team {0}.".format(teamname) )
            team.delete()
        continue

    # Add the team to the repo.
    success = False
    try:
        logger.info("Attempting to add team {0} to repo {1}.".format(teamname, reponame) )
        if team.has_repository(repo):
            logger.warning("Team {0} already has access to repo {1}.".format(teamname, reponame) )
            success=True
            
        else:
            logger.info("Adding repo {0} to team {1}.".format(reponame,teamname) )
            success = team.add_repository(str(repo) )
    
    except:
        success = False
        logger.error("Failed to add repo {0} to team {1}:\n{2}".format(reponame,teamname,traceback.format_exc() ) )

    if not success:
        print("Failed to add team {0} to repo {1}".format(teamname,reponame) )
        if teamadded:
            logger.debug("Removing team {0}.".format(teamname) )
            team.delete()
        if repoadded:
            logger.debug("Removing repo {0}.".format(reponame) )
            repo.delete()
        continue
