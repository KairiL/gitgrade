core-scripts
============

These Python programs provide classes that aim to be used in multiple classes.  A particular course will write additional classes to address needs of those assignments, but use these to do much of the work of dealing with GitHub.

The other repositories in this organization ([https://github.umn.edu/umn-csci-gitscripts/5980-grading-scripts] and umn-csci-F15C5106, for example) provide some examples.

## Scripts versus Programs
The files here need to be seen as programs, software that is developed to be used multiple times.

### Testing
I would like to see some form of testing for these that can be done without too much trouble.  Perhaps creating a "test course" that provides multiple examples of testing scripts and also sample repositories with work in varying states of completeness and functionality.

### Dependencies
These scripts rely on some other Python libraries:
* github3.py
* pexpect (which is now installed on CS/CSE lab machines, I believe)
* plumbum
* requests
* sh
* uritemplate

These can be cloned from a single repo as explained in GettingStarted.md


### Interacting with github.umn.edu
Currently it is only small parts of these scripts use the github3 API.  Other scripts run ``git`` through the command line interface using the ``sh`` package. It might be worthwhile changing these to use this libary instead.  It seems safer and may avoid some of the cumbersome issues when trying to detect and fix bugs when using ``sh``.



## Web-hooks
The real goal of this effort is to get a system in place that can do some automatic assessment of a student's work as soon as it is ``push``ed to GitHub.  There are pieces of this work in this repository, but it may be more important to first get the core scripts in good shape and then move on to this.

