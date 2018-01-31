import logging, traceback, sys, os, errno

LEVELS = { 
    'debug':logging.DEBUG,         # Output relating to data debugging data.
    'info':logging.INFO,           # Output relating to successful completion of some operation.
    'warning':logging.WARNING,     # Output relating to an unexpected event that should not impact execution of the script.
    'error':logging.ERROR,         # Output relating to a recoverable error.
    'critical':logging.CRITICAL    # Output related to an unrecoverable error.
}

SETUP = False
def getLogger(loglevel,logfile=None):
    global SETUP
    global LEVELS
    try:
        if not SETUP:
            directory = os.path.dirname(logfile)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            logging.basicConfig(level=LEVELS.get(LEVELS[loglevel], logging.DEBUG),
                filename=logfile,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M')
            SETUP = True
        return logging.getLogger(__name__)
    except:
        print("Failed to start logger:\n%s" % (traceback.format_exc()))
        sys.exit(1)
        return None

def wellFormedLogLevel(loglevel):
    global LEVELS
    for level in LEVELS:
        if level == loglevel:
            return True
            break
    return False

def getLogLevels():
    global LEVELS
    return LEVELS.keys()
