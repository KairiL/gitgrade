# TestClass-grading-scripts
This is the directory for your new grading scripts. By default this directory should include a couple simple tests for a fake Hwk_00 assignment.  It is recommended that you have your students treat this as an real assignment to get everyone adjusted to the grading script setup.

You can use the Hwk_00_Tests.py and Batch_Hwk_00.py files as templates for future grading assignments.  The core-scripts directory contains additional tests and tools for creating tests.

### Adding active assignments
First you will want to create a new `Hwk_##_Tests.py` file similar to the one provided, where ## is your new assignment number.  For automated feedback by gitbot you will want to create a `Hwk_##_Feedback.py`.  For full assessment you will want to do the same for `Hwk_00_Assess.py` and `Hwk_00_Batch.py`. 

Once you have created these new files you will want to add your new assignment number to active assignments in `Course.py` and `Go.py`. You will want to add your assignment number to the `active_ass_nums` list to the `course` class in `Course.py`.  Then in `Go.py` modify the `feedbacks` dictionary to include your new assignment number in the same format as `Hwk_00_Feedback` as well as add the new `Hwk_##_Feedback` file to the import list.
