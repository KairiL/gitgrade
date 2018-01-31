import datetime, sys, traceback, getpass
import config
import logger
sys.path.append("{0}/dependencies/github3.py".format(config.gitgrade_path) )
sys.path.append("{0}/dependencies/uritemplate".format(config.gitgrade_path) )
import github3


def createTeam(org, team_name, log, debugging=False):
    """
    Create github team named <team_name> within github organization <org>
    """
    team = None
    success = False

    for t in org.teams():
        if t.name == team_name:
            log.info('Team "{0}" already exists.'.format(team_name) )
            if debugging:
                print('Team "{0}" already exists.'.format(team_name) )
            team = t
            success = True

    if team is None:
        try:
            log.info("No {0} team found, creating one.".format(team_name) )
            if debugging:
                print("No {0} team found, creating one.".format(team_name) )
            team = org.create_team(team_name,[],"push")
            success = True
        except:
            team = None
            log.error('Failed during team creation process for team {0}:\n'.format(team_name ) )
            log.debug(traceback.format_exc() )
            if debugging:
                print('Failed during team creation process for team {0}:\n'.format(team_name ) )
                print(traceback.format_exc() )

    if not success:
        print('Failed during team creation process for team {0}:\n{1}'.format(team_name, traceback.format_exc() ) )
    return team

def addUIdToTeam(org, team, uid, log, debugging=False):
    """
    Add student ID <uid> to team named <team_name> inside of github organization <org>
    """
    success = False
    try:
        log.info('Attempting to add {0} to team {1}.'.format(uid, team.name) )
        if team.is_member(uid):
            log.warning('Uid {0} is already a part of team {1}.'.format(uid, team.name) )
            success = True
        else:
            log.info('Adding {0}.'.format(uid) )
            team.invite(uid)
            success = True
    except:
        log.error('Failed to add {0} to team {1}:\n{2}'.format(uid, team.name, traceback.format_exc() ) )
        success = False

    return success

def createRepo(org, team, repo_name, log, debugging=False):
    """
    Create repo named <repo_name> inside of github team <team> 
    inside of github organization <org>
    """
    repo = None
    repo_added = False
    success = False

    for r in org.repositories():
        if r.name == repo_name:
            log.info('Repo "{0}" already exists.'.format(repo_name) )
            repo = r
            success = True
            repo_added = False
    if repo is None:
        try:
            log.info('Creating repo {0}'.format(repo_name) )
            repo = org.create_repository(repo_name,
                                    description = '',
                                    homepage = '',
                                    private = True,
                                    has_wiki = True,
                                    auto_init = True,
            )
            repo_added = True
            success = True
        except:
            log.error('Failed to create repo {0}:\n'.format(repo_name) )
            log.debug(traceback.format_exc() )
            print(traceback.format_exc() )
            repo = None
    if repo:
        success = False
        try:
            log.info('Attempting to add team {0} to repo {1}.'.format(team.name, repo_name) )
            if team.has_repository(repo):
                log.warning('Team {0} already has access to repo {1}.'.format(team.name, repo_name) )
                success = True
            else:
                log.info('Adding team {0} to repo {1}.'.format(team.name, repo_name) )
                success = team.add_repository(str(repo) )
        except:
            success = False
            log.error('Failed to add team {0} to repo {1}:\n'.format(repo_name, team.name ) )
            log.debug(traceback.format_exc() )
        if not success:
            print ('Failed to add team {0} to repo {1}:\n'.format(repo_name, team.name ) )
            if debugging:
                print(traceback.format_exc() )
    
def updateStudentRepos(org_name,
                        uids, 
                        user=getpass.getuser(),
                        password=None,
                        team_format='team-{uid}',
                        repo_format='repo-{uid}',
                        log_level='warning',
                        log_file=str(datetime.datetime.today() ) ):
    """
    Create teams for each student ID in <uids> and add each u_id to their 
    respective teams inside of github organization named <org_name> 
    """
    debugging=(log_level=='debug')
    log=logger.getLogger(log_level, log_file)
    while not password:
        password = getpass.getpass('Password for {0}: '.format(user) )
    github='https://github.umn.edu'
    gh = None
    try:
        enterprise = github3.GitHubEnterprise(github, user, password)
        stats = enterprise.admin_stats('all')
        gh = enterprise
    except:
        gh = None
        log.critical("Failed to log in as user {0}:\n".format(user) )
        log.debug(traceback.format_exc() )
        print("Could not connect or log in to server.")        
        sys.exit(1)

    try:
        org = gh.organization(org_name)
    except:
        log.critical('Problem accessing organization {0}:\n'.format(org_name) )
        log.debug(traceback.format_exc() )
        if debugging:
            print(traceback.format_exc() )
        sys.exit(1)

    if not org:
        log.critical('Problem accessing organization {0}:\n'.format(org_name) )
        sys.exit(1)
    elif debugging:
        log.debug("Organization accessed successfully.")
    
    for uid in uids:
        log.info('Starting setup for {0}.'.format(uid) )

        # Build team and repo names from format string and uid.
        interpolationvalues = { 'uid' : uid }
        team_name = team_format.format(**interpolationvalues)
        repo_name = repo_format.format(**interpolationvalues)
        
        team = createTeam(org, team_name, log, debugging)
        if not team:
            print("Failed to create team {0}, ignoring setup for {1}.".format(team_name, uid) )
        else:
            addUIdToTeam(org, team, uid, log)
            createRepo(org, team, repo_name, log)
                
