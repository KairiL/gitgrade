import argparse
import logger
from getpass import getuser
import datetime#, dateutil.parser

def __checkLogLevel(loglevel):
    if not logger.wellFormedLogLevel(loglevel):        
        msg = ("Log level must be one of the following: {0}".format(logger.getLogLevels()))
        raise argparse.ArgumentTypeError(msg)
    return loglevel
"""
def __checkDueDate(date):
    if dateutil.parser.parse(date) == None:
        raise argparse.ArgumentTypeError("Invalid due date.")
    return date
"""

def getDefaultOptions(description,user=False):
    ''' All github scripts will have some shared options requirements, 
    this function will capture those and allow other scripts to get retrieve 
    them.'''

    parser = argparse.ArgumentParser(description)
    # TODO: Perhaps at some later point we can add options to generate and get oauth tokens.
    # Doing that will require a username and password to be supplied.
    if user:
        parser.add_argument("-u","--user"
                            , help="A github username."
                            , default=getuser(),type=str)
    else:
        parser.add_argument("-o"
                            , "--oauth"
                            , help="The OAuth token to use."
                            , required=True
                            , dest='oauth'
                            , type=argparse.FileType('r'))

    parser.add_argument("-l"
                        , "--loglevel"
                        , help=('Specify the log level. Possible values are: {0}'.format(logger.getLogLevels()))
                        , default='debug'
                        , dest='loglevel'
                        , type=__checkLogLevel)
    parser.add_argument("--logfile"
                        , help='File to store logging information.'
                        , default=None
                        , type=argparse.FileType('w'))
    parser.add_argument("--github",help='The github url to use.'
                        , default='https://github.umn.edu')
    parser.add_argument("--org"
                        , help=("The organization the operations"
                                +" will be performed in.")
                        , dest='org'
                        , type=str
                        , default="umn-rl-101F16")
    """
    parser.add_argument("--duedate"
                        , help=("If specified will find the last commit prior"
                                +" to this date. The date must have the"
                                +" following format: YYYY-MM-DDTHH:MM:SSZ."
                                +" The 'T' and 'Z' are constants that should"
                                +" be left in the date and the hour should be"
                                +" modulo 24.")
                        , dest='duedate'
                        , type=__checkDueDate
                        , default=None)
    """
    return parser

