documentation = ''' 
This file provides an abstract class for a grading session (called
Session) that is to be subclassed for specific grading activities.

It also defines an abstract class for the action (called Action) that
can also be subclassed and provides the functionality to be carried
out in the on individual repositories when grading.  It has a 'run'
method that does the grading work.

'''

import os
import sys
import inspect
import logging

def init():
    '''Initialize library search path and other things.'''

    # Add additional dependencies relative to the real location of this file.
    # BUG: If this file is symlinked all bets are off.
    dependencies = [ "/dependencies/uritemplate", "/dependencies/requests",
                     "/dependencies/github3.py", "/dependencies/sh"]

    for dep in dependencies:
        cmd_subfolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])+dep)
        if cmd_subfolder not in sys.path:
            sys.path.insert(0, cmd_subfolder)

# Run the initialization process when this module is loaded.
# This will only happen the first time it is loaded.
init()

# These imports depend on init() running.
from sh import git, rm
from getpass import getuser


class Assignment():
    '''This abstract class is for "grading sessions" and controls
       the process of cloning each repo and performing the Action
       on it.'''

    # Some needed values have reasonable defaults, and they
    # are specified as field with initial values below.

    user = getuser()
    org = "UNKNONW-ORG"
    github_https = 'https://github.umn.edu'
    github = 'git@github.umn.edu'
    # test file contains grading info
    test_file = "not_specified.txt"
    # name of assessment file
    assessment_file = "not_specified.md"

    uiids = []
    action = 0

    def __init__(self, action, uiids, logger):
        self.action = action
        self.uiids = uiids
        self.grading_dir = os.path.dirname(self.test_file)
        self.test_file = os.path.basename(self.test_file)
        self.logger = logger

    def clone(self):
        '''Clone the repo for all uiids.'''

        for uiid in self.uiids:
            cloneurl_https = "%s/%s/repo-%s.git" % (self.github, self.org, uiid)
            cloneurl = "%s:%s/repo-%s.git" % (self.github, self.org, uiid)
            self.action.clone(uiid,cloneurl,self.logger)

    def sendInfo(self):
        self.action.getAllInfo(self.grading_dir, self.test_file, self.logger, self.assessment_file)


    def run(self):
        '''Run the action of all uiids.'''
        cwd = os.getcwd()
        for uiid in self.uiids:
            self.action.run(uiid, "%s/repo-%s/" %(cwd, uiid))

    def prepareTests(self):
        self.action.prepareTests()

    def clean(self):
        for uiid in self.uiids:
            self.action.clean(uiid)

    def commit(self):
        '''Commit the results for all uiids.'''
        cwd = os.getcwd()
        for uiid in self.uiids:
            self.action.commit(uiid, "%s/repo-%s" %(cwd, uiid))

    def push(self):
        '''Push the results for all uiids.'''
        cwd = os.getcwd()
        for uiid in self.uiids:
            self.action.push(uiid, "%s/repo-%s" %(cwd, uiid))


class Action():
    '''An abstract class for actions to be applied to every
       repository'''

    # Some needed values do not have reasonable defaults, and they
    # should probably be passed as required argument, but we will
    # just set them as fields as well.


    def __init__(self):
        '''Initialize an object'''
        pass


    def clone(self, uiid, cloneurl, logger):
        try:
            rm("-Rf", "repo-%s" % uiid)
        except:
            logger.error("Possibly removing existing repository %s"%uiid)

        logger.info("Cloning %s"%uiid)

        try:
            git("clone", cloneurl)
        except:
            logger.error("Exception cloning %s" %cloneurl)


    def run(self, uiid, repo_path):
        '''run it'''
        print ("Doing nothing intersting for uuid %s in path." % 
               (uiid, repo_path))


    def commit(self, uiid, repo_path, msg):
        '''Commit changes to repo.'''
        pass


    def push(self, uiid, repo_path):
        '''Push result, perhaps.'''
        pass

