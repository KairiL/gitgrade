Some notes about Python script for managing GitHub ...

a test
----------------------------------------------------------------------
-- Setting up sub-modules
-------------------------
For new course you may want to create a repository to store the
scripts and data (e.g. testcases) that will be used in assessment
of programs in your course.  Call this repository Csci101-Fall15

These scripts will want to use the library of scripts in the
repository CORE and thus this CORE repository will be a "submodule" of
your CSci101-Fall15 repository.
 
Start by cloning the repository to which you want to add submodules.

Then add the submodule and optionally the directory in which to keep
it.

% git submodule add https://github.umn.edu/github-scripts/core-scripts.git

% git status
- tell us that a new directory "core" has been added and that
  .gitmodules has changed.


Then commit and push the changes.

----------------------------------------------------------------------
-- Cloning a repository with submodules
---------------------------------------
After setting the submodules in the previous clone, it is easier to
simply delete that clone and make another clone to include the
sub-modules. 

To do this, use the following command:

% get clone --recursive git@github.umn.edu:umn-csci-5161S15/github-scripts.git

This pulls down all the submodules and their contents.  If you leave
off the --recursive flag you only get the directories and not their
contents and have to go to the directories and run extra steps there.


----------------------------------------------------------------------
-- Using a repository with submodules
-------------------------------------

+++ Getting changes made to the submodules

* when someone makes changes to the submodules, you may want those
* go to the submodule directory and do the following:
% git fetch
% get merge origin/master

Better might be the following:
% git submodule update --remote <name of submodule???>


Making modifications to the submodule

In the submod directory

% git checkout master
.. make changes
% git commit
% git push





