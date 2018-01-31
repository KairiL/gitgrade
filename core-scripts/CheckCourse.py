import sys, os
from getpass import getpass, getuser
import config
sys.path.append("{0}/dependencies/github3.py".format(config.gitgrade_path) )
sys.path.append("{0}/dependencies/uritemplate".format(config.gitgrade_path) )
import github3

def gitConnect(user, password, org_name):
    """
    Login to github enterprise.
    Returns a list consisting of the github enterprise object and 
    github organization named org_name
    """
    gh = None
    try:
        enterprise = github3.GitHubEnterprise('https://github.umn.edu', user, password=password)
        stats = enterprise.admin_stats("all")
        gh = enterprise
    except:
        gh = None
        print("Could not connect or login to server.\n");
        sys.exit(1)

    success=False
    # Enter organization
    org=None

    try:
        print("Accessing organization: {0}\n".format(org_name))
        org = gh.organization(org_name)
    except:
        print("Problem accessing organization {0}:\n".format(org_name))
        sys.exit(1)

    if not org:
        print("Organization {0} does not exist or you do not have access rights\n".format(org_name))
        sys.exit(1)
    
    return [gh, org]

def gitBotIn(github, organization, bot_name='robot006'):
    """
    Takes in a github enterprise object and github organization object
    returns True if 'robot006' is in the organization. False otherwise
    """
    return github.user(bot_name) in organization.members(role='admin')

def repoExists(repo_name, organization):
    return repo_name in [repo.name for repo in organization.repositories()]

def getLogin():
    #first attempts to use git config user. If that fails, use local username
    try:
        login = git("config", "user.login")
    except:
        try:
            login=getuser()
            print("used local user: {0}\n".format(login) )
        except:
            print('could not retrieve username automatically')
    while not login:
        login=input("Please enter GitHub login:")
    return login

def runTests():
    login=getLogin()
    password = ''
    while not password:
        password = getpass('GitHub password for {0}: '.format(login))
    org_name = ''
    while not org_name:
        org_name = input('Please enter organization name: ')
    
    [github, org]=gitConnect(login, password, org_name)
    if gitBotIn(github, org,):
        print("Gitbot is an owner.  Passed!")
    else:
        print("Gitbot is not an owner! Add robot006 to your organization as an owner")
    
    for repo_name in ['grading-scripts']:
        if repoExists(repo_name, org):
            print('{0} repo exists.  Passed!'.format(repo_name) )
        else:
            print('You still need to create repo {0}'.format(repo_name) )
    
    if os.path.exists('{0}/core-scripts'.format(config.gitgrade_path) ):
        print ('core-scripts exists.  Passed!')
    else:
        print ('You still need to clone repo "core-scripts"!')

    if os.path.exists('{0}/core-scripts'.format(config.gitgrade_path) ):
        print ('grading-scripts exists.  Passed!')
    else:
        print ('You still need to clone repo "grading-scripts"!')

    if os.path.exists('{0}/dependencies'.format(config.gitgrade_path) ):
        print ('dependencies exists.  Passed!')
    else:
        print ('You still need to clone repo "dependencies"!')
    
runTests()
