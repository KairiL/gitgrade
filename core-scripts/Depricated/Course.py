#!/usr/bin/python3

import sys

class Course:
    def __init__(self):
        self.name = None
        self.title= None
        # absolute paths to directories that hold (perhaps
        # sub-directories) containing student repos during grading,
        # grading results (CSV files), and log files.
        self.grading_home_dir = None 
        self.logging_home_dir = None

        self.github_org = None
        self.github_ssh = None

        self.sample_uiids = None
        self.few_uiids = None
        self.all_uiids = None

        self.log_level = "warning"

    def initialize_grading_dir(self):
        pass
