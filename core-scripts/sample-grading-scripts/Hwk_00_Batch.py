#!/usr/bin/env python3
import os
import logging
import datetime
import sys, subprocess

import config
from sh import git, cat, echo

import Batch, Test, Action

import Course, Hwk_00_Assess, Hwk_00_Tests
            
if __name__ == "__main__":
    b = Batch.BatchRun( Course.course(), Hwk_00_Assess.Hwk_00_Assess() )
    b.run_specific (['user100'], True)
