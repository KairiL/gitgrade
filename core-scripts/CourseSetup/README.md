CourseSetup
===============
Course Setup repo

##New Course Setup
0. If this is your first time setting up a course edit CourseSetup/config.examp to refer to your gitgrade directory and save it as config.py.

1. Fill out 'CourseSetup/new_course.csv' with the following fields and save.  Do not place quotes around values inside cells.  Fields with multiple values should have each value placed in a separate cell in that field's row. Use only alphanumeric characters to avoid errors with python and github.

__title__
The full title of your course, e.g. "RL 101: Paid Suffering"

__department__
The abbreviation for your department, e.g. "csci"

__course_number__
The 3 or 4 digit number assigned to this course, e.g. "2021"

__session__ 
The school term for this course, e.g. "Sp", "F", "Su"

__year__ 
The year during which this course runs, e.g. "16", "2017"

__Section__
The section number. This field can be left blank if all sections are graded based on the same criteria.
Starting with a number may lead to a confusing course name, but is valid
e.g. "S01", "Sec01", "grads", "kidsIhate". 

__instr_uiids__
UMN/github accounts for Instructors, i.e. x500 or equivalent separated by cell
e.g. "jones0001", "jones0001"|"kai"|"doexx042"

__TA_uiids__
UMN/github accounts for teaching assistants, i.e. x500 or equivalent, separated by cell
e.g. "jones0001, kai, doexx042"

__grad_uiids__
UMN/github accounts for graduate students enrolled in this course, i.e. x500 or equivalent, separated by cell

__ugrad_uiids__
UMN/github accounts for undergrad students enrolled in this course, i.e. x500 or equivalent, separated by cell

__sample_uiids__
Sample accounts for testing separated by cell.  These do not need to be real UMN/Github accounts

2. Run "python3 CreateCourse.py" from the CourseSetup directory and enter your github credentials when prompted.  If you receive an error about python3 run "module load soft/python/anaconda" before trying again. You should be given an organization name.  Create a new organization in GitHub with this name and add robot006 (or whatever your gitbot is named) as an owner. To set robot006 as an owner go to the "People" tab of the new organization and change "Member" to "Owner".

3. In new github organization click on the "Settings" tab and on the left click "Member Privileges" and change "Default repository permission" to "None" and click "Save". 

4. While still in the settings menu click "Hooks" on the left side and "Add webhook" on the top right.  Fill out Payload URL and submit with the "Add webhook" button.  If you do not know the payload URL and port contact Kairi Lassard at lassa005@umn.edu or Eric Van Wyk at evw@umn.edu

5. Run "python3 CreateCourse.py" from the CreateCourse directory again. Enter your password for your github account when prompted.

6. Do a happy dance.  You're ready to grade some homework!
