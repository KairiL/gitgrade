#!/usr/bin/env python3
import sys, getpass, datetime
import config, Course
sys.path.append ("{0}/core-scripts/".format(config.gitgrade_path) )
sys.path.append ("{0}/core-scripts/CourseSetup".format(config.gitgrade_path) )
import TeamSetup


org_name=Course.course.github_org
uids=Course.course.all_uiids
user=getpass.getuser()
password=None
team_format='team-{uid}'
repo_format='repo-{uid}'
log_level='debug'
log_dir=Course.course.logging_home_dir
log_file='{0}/{1}.log'.format(log_dir, str(datetime.datetime.today() ) )

TeamSetup.updateStudentRepos(org_name,
                            uids, 
                            user,
                            password,
                            team_format,
                            repo_format,
                            log_level,
                            log_file
)
