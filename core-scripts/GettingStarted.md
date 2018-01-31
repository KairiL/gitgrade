Getting Started
===============

There are two primary tasks with which these programs aim to assist.  
First is setting up repositories for students.  
Second is with assessing student programming assignment by running tests.  
This second goal is not meant to replace manual inspection of assignments, in fact it aims at 
providing TAs and instructors with more time to do it since these programs can automate
the repetitve and uninteresting aspects of grading.

Below are the steps an instructor or TA should take to set up the repositories to begin working with the programs.


### Clone 2 repositories
1. `git clone git@github.umn.edu:umn-csci-gitscripts/core-scripts.git`
2. `git clone git@github.umn.edu:umn-csci-gitscripts/dependencies.git`

These contain, respectively, the shared classes and functions for the two goals 
mentioned above and some external Python libraries that are used by the "core" programs.

The resulting directories need to be siblings to each other, and to other repositories described below.  
The document assumes that these are cloned into a directory named `Grading`, but this specific name
is not required.

### Create organziation for course
On https://github.umn.edu, create an "organization" for your course.  Traditionally organizations are named in a standardized way with the following template *umn-csci-XXXXSYY* where *XXXX* is the four digit number of the course, *S* is "F" or "S" for fall or spring semester, and "YY" is the last two digits of the year.  Other possibilities are supported, but some find a standarized naming system helps keep thing straight.

### Change some settings
In new github organization click on the "Settings" tab and on the left click "Member Privileges" and change "Default repository permission" to "None" and click "Save".

### Create a grading-scripts repository
Next create a repository in this organization named `grading-scripts`.  The programs in the `core-scripts` repository require this name. 

### Clone this repository
Clone this `grading-scripts` into your `Grading` directory so that it is a siblig to `core-scripts` and `dependencies`.  This organization is required by the programs.

### Copy sample grading scripts
Copy the contents of `core-scripts/sample-grading-scripts` into your new `grading-scripts` repository.

### Modify grading-scripts files
Modify the properties in Course.course to match your course details, including title, name, instr_uiids, TA_uiids,  grad_uiids, ugrad_uiids, logging_home_dir, and github_org

### Enable Organization Webhooks
Add robot006 as an owner to the new organization.  Then go to Settings -> Hooks -> Add webhook.  The Payload URL will be paladin.cs.umn.edu:8083

### Push your updates to github
Add all of your new files in `grading-scripts` to github.  Commit and push these files so they can be cloned by gitbot.

### Create Student Repositories
In your grading-scripts directory run "python3 UpdateStudentRepos.py".  This will create repositories for all of your students.  This can be run again if you add more students to one of your *_uiids lists.

### Add gitbot to your course group?
