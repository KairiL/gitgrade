'''
Tests.py contains classes and functions for specifying and running tests.
These classes should serve as both a model and building blocks for your
own tests.  
'''
import os, sys, subprocess, logging, datetime, re

import config
sys.path.append ('{0}/dependencies/sh/'.format(config.gitgrade_path))
import sh
from sh import cat, ls, cp, mv
#sys.path.append ('{0}/dependencies/pexpect/'.format(config.gitgrade_path))
import pexpect
# Classes and functions for specifying and running tests.
from functools import reduce

from Util import strip, stripLast, wrap, indent

# Two main component here:
# 1. ResultReport - represents the results of running a test
# 2. Test - abstract class for various tests.

# An enumerated type for test result types.
class ResultType:
    testpass = 1
    testfail = 2
    testnotrun = 3

# A class for test results, used to generate Markdown report and CSV file.
class ResultReport:
    def __init__(self, result, score, possible, description):
        self.resultType = result
        self.score = score
        self.possible = possible
        self.description = description
        self.reportScore = True 

    def passed(self):
        return (self.resultType == ResultType.testpass)

    # TODO: add a flag to distinguish Grading from Feedback.  Then feedback
    # reports can elect to not generate scores, just pass/fail messages.
    def show(self, forAssessment):
        s = "+ "
        if forAssessment:
            s += " _{0}_ / _{1}_ : ".format(self.score, self.possible)

        if   self.resultType == ResultType.testpass:
            s += "Pass: {0}".format(self.description)
        elif self.resultType == ResultType.testfail:
            s += "Fail: {0}".format(self.description)
        elif self.resultType == ResultType.testnotrun:
            s += "Skip: {0}\n\n".format(self.description)
            s += "  This test was not run because of an earlier failing test."
        else:
            s += "Error: {0}\n\n".format(self.description)
            s += "  Test result recorded incorrectly.  See the TA."

        s += "\n\n"
        return s


class TotalScoreReport(ResultReport):
    def __init__(self):
        self.score = 0
        self.possible = 0
        self.reportScore = True 

    def show(self, forAssessment):
        return ( "#### Total score: _%s_ / _%s_\n\n" % (self.score, self.possible) )
        

# A class for messages that are not really tests.
class MsgReport(ResultReport):
    def __init__(self,msg):
        self.msg = msg
        self.score = 0
        self.possible = 0
        self.reportScore = False

    def passed(self):
        return True

    def show(self, forAssessment):
        return "%s\n\n" % self.msg

class ManualReport:
    def __init__(self, description, possible):
        self.possible = possible
        self.description = description
        self.score = 0
        self.possible = 0

    def passed(self):
        return (True)

    # TODO: add a flag to distinguish Grading from Feedback.  Then feedback
    # reports can elect to not generate scores, just pass/fail messages.
    def show(self, forAssessment):
        s = "+ "
        if forAssessment:
            s += " ____ / _%s_ : " % self.possible

        s += "%s\n\n" % self.description
        return s

class Test():
    description = "Abstract test class."
    doNotReportWhenNotRun = False
    def run(self):
        '''Perform the test activities and return results.'''
        return [ ResultReport(ResultType.testpass, 0, 10, "") ]

    def not_run_desc(self):
        '''A description for tests that were not run.'''
        if self.doNotReportWhenNotRun:
            return [ ]
        else:
            return [ ResultReport(ResultType.testnotrun, 0, self.possible, self.description) ]
        # "This test not run because of an earlier failure: %s" % 


class FailingSequenceTest(Test):
    '''A sequence of tests that terminate on the first failing test.'''

    description = "A test sequence that aborts on the first failure."

    def __init__(self, ts):
        self.tests = ts

    def run(self):
        results = []
        keep_testing = True
        for t in self.tests:
            if keep_testing:
                t_results = t.run()
                num_tests = len(t_results)
                if num_tests > 0:
                    last_res = t_results[-1]
                    logging.info ("Ran %s" % last_res.passed())
                    if not last_res.passed():
                        logging.info ("Test failed")
                        keep_testing = False
            else:
                t_results = t.not_run_desc()
            results.extend(t_results)
        return results

    def not_run_desc(self):
        results = []
        for t in self.tests:
            t_results = t.not_run_desc()
            results.extend(t_results)
        return results


class SequenceTest(Test):
    '''A sequence of tests that all execute, regardless of failure of any test.'''

    description = "A test sequence that runs all tests, regardless of failure."

    def __init__(self, ts):
        self.tests = ts

    def run(self):
        results = []
        for t in self.tests:
            t_results = t.run()
            results.extend(t_results)
        return results

    def not_run_desc(self):
        results = []
        for t in self.tests:
            t_results = t.not_run_desc()
            results.extend(t_results)
        return results


class ChoiceTest(Test):
    '''A test sequence that passes on the first success.'''

    description = "A test sequence that passes on the first success."

    def __init__(self, ts):
        self.tests = ts

    def run(self):
        results = []
        for t in self.tests:
            t_results = t.run()
            num_tests = len(t_results)
            if num_tests > 0:
                last_res = t_results[-1]
                logging.info ("Ran %s" % last_res.passed())
                if last_res.passed():
                    logging.info ("Test passed")
                    keep_testing = False
                    return results
            results.extend(t_results)
        return results

    def not_run_desc(self):
        results = []
        for t in self.tests:
            t_results = t.not_run_desc()
            results.extend(t_results)
        return results


# Sample File System Tests
# --------------------------------------------------
class FileOrDirectoryExists(Test):
    def __init__(self, name, fileOrDir, possible):
        self.filename = name
        self.possible = possible
        self.description = "Check that %s \"%s\" exists." %  \
                              (fileOrDir,self.filename)

    def run(self):
        if "directory" in self.description:
            if os.path.exists(self.filename):
                return [ ResultReport(ResultType.testpass, self.possible, self.possible, 
                          self.description) ]
            else:
                return [ ResultReport(ResultType.testfail, 0, self.possible,
                                      self.description + "\n\n     \"%s\" not found." % self.filename ) ]
        else:
            if os.path.isfile(self.filename):
                return [ ResultReport(ResultType.testpass, self.possible, self.possible, 
                          self.description) ]
            else:
                return [ ResultReport(ResultType.testfail, 0, self.possible,
                                      self.description + "\n\n     \"%s\" not found." % self.filename ) ]

class FileExists(FileOrDirectoryExists):
    def __init__(self, filename, possible):
        FileOrDirectoryExists.__init__(self,filename, "file", possible)

class DirectoryExists(FileOrDirectoryExists):
    def __init__(self, dirname, possible):
        FileOrDirectoryExists.__init__(self,dirname, "directory", possible)

# Monadic 'bind' to whichever of the given names exists
class FileOrDirectoryChoice(Test):
    def __init__(self, names, fileOrDir, possible, test_fn):
        self.filenames = names
        self.possible = possible
        self.test_fn = test_fn
        self.description = "Check that one of %ss %s exists." %  \
                              (fileOrDir,str(self.filenames))

    def run(self):
        if "directory" in self.description:
            for name in self.filenames:
                if os.path.exists(name):
                    return [ ResultReport(ResultType.testpass, self.possible, self.possible, 
                                          self.description) ] + self.test_fn(name).run()
            return [ ResultReport(ResultType.testfail, 0, self.possible,
                                  self.description + "\n\n     None of %s found." % str(self.filenames) ) ] \
                + self.test_fn("<undetermined>").not_run_desc()
        else:
            for name in self.filenames:
                if os.path.isfile(name):
                    return [ ResultReport(ResultType.testpass, self.possible, self.possible, 
                                          self.description) ] + self.test_fn(name).run()
            return [ ResultReport(ResultType.testfail, 0, self.possible,
                                  self.description + "\n\n     None of %s found." % str(self.filenames) ) ] \
                + self.test_fn("<undetermined>").not_run_desc()

    def not_run_desc(self):
        return [ ResultReport(ResultType.testnotrun, 0, self.possible, self.description) ] \
            + self.test_fn("<undetermined>").not_run_desc()

class FileChoice(FileOrDirectoryChoice):
    def __init__(self, filenames, possible, test_fn):
        FileOrDirectoryChoice.__init__(self,filenames, "file", possible, test_fn)

class DirectoryChoice(FileOrDirectoryChoice):
    def __init__(self, dirnames, possible, test_fn):
        FileOrDirectoryChoice.__init__(self,dirnames, "directory", possible, test_fn)


class ChangeDirectory(Test):
    def __init__(self, dirname, possible):
        self.dirname = dirname
        self.possible = possible
        self.description = "Change into directory \"%s\"." % dirname

    def run(self):
        try:
            os.chdir(self.dirname)
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, 
                      self.description) ]
        except:
            return [ ResultReport(ResultType.testfail, 0, self.possible, 
                                  self.description + "\n\n     Directory \"%s\" not found." % self.dirname ) ]



class TotalScoreTest(Test):
    def  __init__(self):
        pass

    def run(self):
        return [ TotalScoreReport() ]

class ManualTestToComplete(Test):
    def __init__(self, desc, possible):
        self.description = desc
        self.possible = possible

    def run(self):
        return [ ManualReport(self.description, self.possible) ]

    def not_run_desc(self):
        return [ ManualReport(self.description, self.possible) ]


class EnterScore(Test):
    '''Enter a score for a result computed elsewhere.'''

    def __init__(self,description,possible):
        self.description = description
        self.possible = possible

    def run(self):

        print ("----------------------------------------------------------------------\n")
        print ("In directory: %s\n" % os.getcwd())
        print ("----------------------------------------------------------------------\n")

        have_score = False
        while not have_score:
            try:
                print ("The problem description....\n")
                print (self.description + "\n\n")

                score = int(input("\n\nEnter number of points (out of %d): " % self.possible))
                have_score = True
            except:
                print("An invalid string was entered.  Try again.\n")


        comment = input("\nEnter a comment for this score: ")
        #comment = "......."
                
        desc = self.description
        desc += "\n\n    "
        desc += comment

        return [ ResultReport(ResultType.testpass, score, self.possible, desc) ]

class EnterFloatScore(Test):
    '''Enter a score for a result computed elsewhere.'''

    def __init__(self,description,possible):
        self.description = description
        self.possible = possible

    def run(self):
        have_score = False
        while not have_score:
            try:
                print ("The problem description....\n")
                print (self.description + "\n\n")

                score = float(input("\n\nEnter number of points (out of %d): " % self.possible))
                have_score = True
            except:
                print("An invalid string was entered.  Try again.\n")


        comment = input("\nEnter a comment for this score: ")
        #comment = "......."
                
        desc = self.description
        desc += "\n\n   "
        desc += comment

        return [ ResultReport(ResultType.testpass, score, self.possible, desc) ]

class EnterGrade(Test):
    '''Enter a grade (or other non-numeric score) for a result computed elsewhere.'''

    def __init__(self,description):
        self.description = description

    def run(self):
        print ("The problem description....\n")
        print (self.description + "\n\n")
        
        grade = input("\n\nEnter the grade: ")
        comment = input("\nEnter a comment for this grade: ")

        return [ MsgReport("Your grade is: %s\n\n%s" % (grade,comment)) ]

class Inspect(Test):
    '''Inspect a file, and enter a score for it.'''

    def __init__(self,filename,description,possible):
        self.filename = filename
        self.description = description
        self.possible = possible

    def run(self):
        if os.path.exists(self.filename):
            print ("\n\n\nShowing contents of %s.\n" % self.filename)
            print ("----------------------------------------------------------------------\n")
            print ("----------------------------------------------------------------------\n")
            subprocess.call(["pwd"])
            print ("----------------------------------------\n")
            subprocess.call(["more", self.filename])
            print ("----------------------------------------------------------------------\n")
            print ("----------------------------------------------------------------------\n")

            subprocess.call(["pwd"])

            have_score = False
            while not have_score:
                try:
                    score = int(input("\n\nEnter number of points for %s (%d): " % (self.filename, self.possible)))
                    have_score = True
                except:
                    print("An invalid string was entered.  Try again.\n")


            comment = input("\nEnter a comment for this score: ")
            #comment = "......."

            desc = self.description
            desc += "\n\n    "
            desc += comment
            return [ ResultReport(ResultType.testpass, score, self.possible, desc) ]

        else:
            print ("\n\nFile %s not found.  Showing directory contents.\n\n" % self.filename)
            print ("----------------------------------------------------------------------\n")
            print ("----------------------------------------------------------------------\n")
            subprocess.call(["pwd"])
            subprocess.call (["ls", "-l"])
            desc = self.description
            desc += "\n\nThe file was not found.\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]



class AddCodeToEnd(Test):
    '''Add some text to the end of a file.'''

    def __init__(self,filename,text):
        self.filename = filename
        self.text = text
        self.possible = 0
        self.description = ("Add declarations to the end of \"%s\" " +
                            "to assist in test for errors.") % filename
        self.doNotReportWhenNotRun = True

    def run(self):
        save_filename = "%s_SAVE" % self.filename
        cp(self.filename, save_filename)
        resfile = open(self.filename, "a")
        resfile.write(self.text)
        resfile.close()
        return []

class CleanUp(Test):
    '''Move files back to their original place'''

    def __init__(self,filename):
        self.filename = filename
        self.possible = 0
        self.description = ("Restore student's original file, %s") % filename
        self.doNotReportWhenNotRun = True

    def run(self):
        save_filename = "%s_SAVE" % self.filename
        mv(save_filename, self.filename)
        return []


# C specific tests
# --------------------------------------------------
class CCompileTest(Test):
    '''Check that a C file compiles.'''
    
    def __init__(self,filenames,binname=None,possible=3,timeout=5):
        self.filenames = filenames
        self.binname = binname
        self.possible = possible
        self.description = "Check that a C file compiles."
        self.timeout=timeout

    def run(self):
        from sh import gcc
        if not isinstance(self.filenames, str):
            filenames = self.filenames
        else:
            filenames = self.filenames,
        try:
            if self.binname:
                res = gcc(*filenames, o=self.binname, _timeout=self.timeout)
            else:
                res = gcc(*filenames, _timeout=self.timeout)
            desc  = self.description
            desc += "\n\n"
            desc += "    C file(s) %s compile with no errors.\n\n" % repr(self.filenames)
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        except sh.ErrorReturnCode:
            desc  = self.description
            desc += "\n\n"
            desc += "    C file(s) %s have errors.\n\n" % repr(self.filenames)
            # ToDo: save error messages and add them to the description
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

# Pascal specific tests
# --------------------------------------------------
class PascalCompileTest(Test):
    '''Check that a Pascal file compiles.'''
    
    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check that a Pascal file compiles."
        self.timeout=timeout

    def run(self):
        from sh import fpc
        try:
            fpc(self.filename, '-o' + self.filename.split('.')[0])
            desc  = self.description
            desc += "\n\n"
            desc += "    Pascal file \"%s\" compiles with no errors.\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        except:
            desc  = self.description
            desc += "\n\n"
            desc += "    Pascal file \"%s\" has errors.\n\n" % self.filename
            # ToDo: save error messages and add them to the description
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

# Java specific tests
# --------------------------------------------------
class JavaCompileTest(Test):
    '''Check that a Java file compiles.'''
    
    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check that a Java file compiles."
        self.timeout=timeout

    def run(self):
        from sh import javac
        try:
            javac(self.filename)
            desc  = self.description
            desc += "\n\n"
            desc += "    Java file \"%s\" compiles with no errors.\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        except:
            desc  = self.description
            desc += "\n\n"
            desc += "    Java file \"%s\" has errors.\n\n" % self.filename
            # ToDo: save error messages and add them to the description
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]


# SML specific tests
# --------------------------------------------------
class SMLTypeCheck(Test):
    '''Check for type correctness of SML program.'''

    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check for type correctness of an SML program."
        self.timeout=timeout

    def run(self):
        # Start SML
        child = pexpect.spawn('sml',timeout=self.timeout)
        child.expect('Standard ML of New Jersey v110')
        child.expect('- ')

        # Load the file
        child.sendline("use \"%s\" ;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*-', 'uncaught exception (.*\r\n)*-', pexpect.TIMEOUT ])

        if i == 0:
            desc  = self.description
            desc += "\n\n"
            desc += "     No syntax or type errors in \"%s\".\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        elif i == 1 or i == 2:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += child.after.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.before)
            desc += "\n\n"
            desc += child.before.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class SMLEvalTest(Test):
    '''Test SML expression evaluates to specified value.'''

    def __init__(self,filename,possible,expr,result,timeout=5,comment=""):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that the result of evaluating %s matches the pattern `%s`.\n\n   %s" % (wrap(expr),result,comment)
        self.timeout=timeout


    def run(self):
        # Start SML
        child = pexpect.spawn('sml',timeout=self.timeout)
        child.expect('Standard ML of New Jersey v110')
        child.expect('- ')

        # Load the file
        child.sendline("use \"%s\" ;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*-', 'uncaught exception (.*\r\n)*-', pexpect.TIMEOUT ])

        if i == 0:
            # send the expression to evaluate
            child.sendline("%s ;" % self.expr)

            # collect the input echoed back
            j = child.expect([ r";[\r\n]*", pexpect.TIMEOUT])

            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all of the output
            try:
                child.expect ("- ")
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                #j = child.expect([("= %s" % self.correct_result), '= false', 'Error(.*\r\n)*-', 
                #               pexpect.TIMEOUT])

                if re.search(self.correct_result, output):
                    # It worked.
                    result = [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                            self.description + "\n\n") ]

                elif re.search("(Error)|(Exception)", output):
                    # Error in evaluation
                    desc  = self.description + "\n\n"
                    desc += "   Test failed. The following errors were reported:\n"
                    desc += wrap(output)
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

                else:
                    # It didn't - just show results.
                    desc  = self.description + "\n\n"
                    desc += "   Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

            except:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Test failed. A timeout (or other exception) occurred before "
                desc += "your code completed.  Please try the problem in your solution "
                desc += "and let Eric know if it does in fact work.\n"
                result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        elif i == 1:
            # Errors in loading the file
            desc  = self.description
            desc += "\n\n"
            desc += "   Errors were found in \".%s\"\n" % self.filename
            desc += "   But this should not happen since we've tested this file already.\n"
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n   "
            desc += child.after.decode()
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "   Unexpected error #3, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n"
            desc += str(child.after)
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        return result

class SMLEvalEqualTest(Test):
    '''Test SML expression evaluates to specified value.'''

    def __init__(self,filename,possible,expr,result,timeout=5,comment=""):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that %s evaluates to `%s` (use `=` to check for equality).\n\n   %s" % (wrap(expr),result,comment)
        self.timeout=timeout

    def run(self):
        # Start SML
        child = pexpect.spawn('sml',timeout=self.timeout)
        child.expect('Standard ML of New Jersey v110')
        child.expect('- ')

        # Load the file
        child.sendline("use \"%s\" ;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*-', 'uncaught exception (.*\r\n)*-', pexpect.TIMEOUT ])

        if i == 0:
            # send the expression to evaluate
            child.sendline("(%s) = (%s) ;" % (self.expr,self.correct_result) )

            # collect the input echoed back
            j = child.expect([ r";[\r\n]*", pexpect.TIMEOUT])

            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all of the output
            try:
                child.expect ("- ")
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                #j = child.expect([("= %s" % self.correct_result), '= false', 'Error(.*\r\n)*-', 
                #               pexpect.TIMEOUT])

                if re.search('true', output):
                    # It worked.
                    result = [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                            self.description + "\n\n") ]

                elif re.search("(Error)|(Exception)", output):
                    # Error in evaluation
                    desc  = self.description + "\n\n"
                    desc += "   Test failed. The following errors were reported:\n"
                    desc += wrap(output)
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

                else:
                    # It didn't work - just show results.

                    # send the expression to evaluate
                    child.sendline("(%s) = (%s) ;" % (self.expr,self.correct_result) )
                    # collect the input echoed back
                    j = child.expect([ r";[\r\n]*", pexpect.TIMEOUT])

                    child.expect ("- ")
                    output = child.before.decode()
                    print ("Collecting the output for incorrect evaluation.\n")
                    print ("Before part:\n%s\n" % child.before.decode())
                    print ("After part:\n%s\n" % child.after.decode())

                    desc  = self.description + "\n\n"
                    desc += "   The equality test failed. Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

            except:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Test failed. A timeout (or other exception) occurred before "
                desc += "your code completed.  Please try the problem in your solution "
                desc += "and let Eric know if it does in fact work.\n"
                result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        elif i == 1:
            # Errors in loading the file
            desc  = self.description
            desc += "\n\n"
            desc += "   Errors were found in \".%s\"\n" % self.filename
            desc += "   But this should not happen since we've tested this file already.\n"
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n   "
            desc += child.after.decode()
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "   Unexpected error #3, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n"
            desc += str(child.after)
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        return result


# OCaml specific tests
# --------------------------------------------------
class OCamlTypeCheck(Test):
    '''Check for type correctness of OCaml program.'''

    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check for type correctness of an OCaml program."
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('ocaml',timeout=self.timeout)
        child.expect('OCaml version .*# ')
        #child.expect('OCaml version 4.01.0.*# ')

        child.sendline("#use \"%s\" ;;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*#', 'Exception:(.*\r\n)*#', pexpect.TIMEOUT ])

        if i == 0:
            desc  = self.description
            desc += "\n\n"
            desc += "     No syntax or type errors in \"%s\".\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        elif i == 1 or i == 2:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += child.after.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.before)
            desc += "\n\n"
            desc += child.before.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class OCamlEvalTest(Test):
    '''Test OCaml expression evaluates to specified value.'''

    def __init__(self,filename,possible,expr,result,timeout=5,comment=""):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that the result of evaluating %s matches the pattern `%s`.\n\n   %s" % (wrap(expr),result,comment)
        self.timeout=timeout


    def run(self):
        # start OCaml
        child = pexpect.spawn('ocaml',timeout=self.timeout)
        child.expect('OCaml version .*# ')
        #child.expect('OCaml version 4.01.0.*# ')

        # load the file
        child.sendline("#use \"%s\" ;;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*#', pexpect.TIMEOUT ])

        if i == 0:
            # send the expression to evaluate
            child.sendline("%s ;;" % self.expr)

            # collect the input echoed back
            j = child.expect([ r";;[\r\n]*", pexpect.TIMEOUT])

            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all of the output
            try:
                child.expect ("# ")
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                #j = child.expect([("= %s" % self.correct_result), '= false', 'Error(.*\r\n)*#', 
                #               pexpect.TIMEOUT])

                if re.search(self.correct_result, output):
                    # It worked.
                    result = [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                            self.description + "\n\n") ]

                elif re.search("(Error)|(Exception)", output):
                    # Error in evaluation
                    desc  = self.description + "\n\n"
                    desc += "   Test failed. The following errors were reported:\n"
                    desc += wrap(output)
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

                else:
                    # It didn't - just show results.
                    desc  = self.description + "\n\n"
                    desc += "   Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

            except:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Test failed. A timeout (or other exception) occurred before "
                desc += "your code completed.  Please try the problem in your solution "
                desc += "and let Eric know if it does in fact work.\n"
                result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        elif i == 1:
            # Errors in loading the file
            desc  = self.description
            desc += "\n\n"
            desc += "   Errors were found in \".%s\"\n" % self.filename
            desc += "   But this should not happen since we've tested this file already.\n"
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n   "
            desc += child.after.decode()
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "   Unexpected error #3, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n"
            desc += str(child.after)
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        return result


class OCamlEvalEqualTest(Test):
    '''Test OCaml expression evaluates to specified value.'''

    def __init__(self,filename,possible,expr,result,timeout=5,comment=""):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that %s evaluates to `%s` (use `=` to check for equality).\n\n   %s" % (wrap(expr),result,comment)
        self.timeout=timeout

    def run(self):
        # start OCaml
        child = pexpect.spawn('ocaml',timeout=self.timeout)
        child.expect('OCaml version .*# ')
        #child.expect('OCaml version 4.01.0.*# ')

        # load the file
        child.sendline("#use \"%s\" ;;" % self.filename)
        i = child.expect([ 'program_load_check', 'Error(.*\r\n)*#', pexpect.TIMEOUT ])

        if i == 0:
            # send the expression to evaluate
            child.sendline("(%s) = (%s) ;;" % (self.expr,self.correct_result) )

            # collect the input echoed back
            j = child.expect([ r";;[\r\n]*", pexpect.TIMEOUT])

            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all of the output
            try:
                child.expect ("# ")
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                #j = child.expect([("= %s" % self.correct_result), '= false', 'Error(.*\r\n)*#', 
                #               pexpect.TIMEOUT])

                if re.search('true', output):
                    # It worked.
                    result = [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                            self.description + "\n\n") ]

                elif re.search("(Error)|(Exception)", output):
                    # Error in evaluation
                    desc  = self.description + "\n\n"
                    desc += "   Test failed. The following errors were reported:\n"
                    desc += wrap(output)
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

                else:
                    # It didn't work - just show results.

                    # send the expression to evaluate
                    child.sendline("(%s) = (%s) ;;" % (self.expr,self.correct_result) )
                    # collect the input echoed back
                    j = child.expect([ r";;[\r\n]*", pexpect.TIMEOUT])

                    child.expect ("# ")
                    output = child.before.decode()
                    print ("Collecting the output for incorrect evaluation.\n")
                    print ("Before part:\n%s\n" % child.before.decode())
                    print ("After part:\n%s\n" % child.after.decode())

                    desc  = self.description + "\n\n"
                    desc += "   The equality test failed. Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

            except:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Test failed. A timeout (or other exception) occurred before "
                desc += "your code completed.  Please try the problem in your solution "
                desc += "and let Eric know if it does in fact work.\n"
                result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        elif i == 1:
            # Errors in loading the file
            desc  = self.description
            desc += "\n\n"
            desc += "   Errors were found in \".%s\"\n" % self.filename
            desc += "   But this should not happen since we've tested this file already.\n"
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n   "
            desc += child.after.decode()
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "   Unexpected error #3, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n"
            desc += str(child.after)
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        return result

# Haskell specific tests
# --------------------------------------------------
class HaskellTypeCheck(Test):
    '''Check for type correctness of Haskell program.'''

    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check for type correctness of Haskell program."
        self.timeout=timeout

    def run(self):
        #print("GHCi Timeout = %s\n" % str(self.timeout))
        child = pexpect.spawn('ghci', timeout=self.timeout)
        child.expect('GHCi, version 7.10.3')

        child.sendline(":l \"%s\"" % self.filename)
        child.expect(".*Compiling.*\r\n")
        i = child.expect(['Ok, modules loaded', 'Failed,(.*\r\n)*', pexpect.TIMEOUT])

        if i == 0:
            desc  = self.description
            desc += "\n\n"
            desc += "     No syntax or type errors in \"%s\".\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += child.before.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class HaskellEvalTest(Test):
    '''Test Haskell expression evaluates to specified value.'''

    def __init__(self,filename,possible,expr,result,timeout=5):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that %s   evaluates to `%s`.\n" % (wrap(expr),result)
        self.timeout=timeout

        file_no_path = os.path.basename(filename)
        file_no_ext = os.path.splitext(file_no_path)[0]
        self.prompt_re = r"(\*Main>)|(\*" + file_no_ext + r">)|(\*" + file_no_ext[0].upper() + file_no_ext[1:] + r">)"

    def run(self):
        # start GHCi
        child = pexpect.spawn('ghci', timeout=self.timeout)
        child.expect('GHCi, version 7.10.3')

        # load the file
        child.sendline(":l \"%s\"" % self.filename)
        child.expect(".*Compiling.*\r\n")
        i = child.expect(['Ok, modules loaded', 'Failed,(.*\r\n)*', pexpect.TIMEOUT])

        if i == 0:
            # send the expression to evaluate
            child.sendline(":{\n%s\n:}\n" % self.expr)

            # collect the input echoed back by GHCi
            j = child.expect([":}[\r\n]*", pexpect.TIMEOUT])
            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all the output.
            j = child.expect([self.prompt_re, pexpect.TIMEOUT])
            if j == 0:
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                if re.search(self.correct_result, output):
                    # It worked.
                    result = [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                            self.description + "\n\n") ]

                elif re.search("<interactive>", output):
                    # Error in evaluation
                    desc  = self.description + "\n\n"
                    desc += "   Test failed. The following errors were reported:\n"
                    desc += wrap(output)
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

                else:
                    # It didn't - just show results.
                    desc  = self.description + "\n\n"
                    desc += "   Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            else:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Your solution took to long to run.  Check that it will always terminate? "
                result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
                


        elif i == 1:
            # Errors in loading the file
            desc  = self.description + "\n\n"
            desc += "   Errors were found in \"%s\"\n" % self.filename
            desc += "   But this should not happen since we've tested this file already.\n"
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n   "
            desc += child.after.decode()
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "   Unexpected error #3, timeout on child.expect for \"%s\"\n\n" % self.filename
            desc += "   Talk to Eric about this.  Errors include:\n"
            desc += "   ```\n"
            desc += str(child.after)
            desc += "\n   ```\n"
            result = [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

        return result

class HaskellInspect(Test):
    '''Inspect the result of a Haskell evaluation, and enter a score for it.'''

    def __init__(self,filename,possible,expr,description,timeout=5):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.description = description
        self.timeout=timeout

        file_no_path = os.path.basename(filename)
        file_no_ext = os.path.splitext(file_no_path)[0]
        self.prompt_re = r"(\*Main>)|(\*" + file_no_ext + r">)|(\*" + file_no_ext[0].upper() + file_no_ext[1:] + r">)"

    def run(self):
        # start GHCi
        child = pexpect.spawn('ghci', timeout=self.timeout)
        child.expect('GHCi, version 7.10.3')

        # load the file
        child.sendline(":l \"%s\"" % self.filename)
        i = child.expect(['Ok, modules loaded', 'Failed,(.*\r\n)*#', pexpect.TIMEOUT])

        if i == 0:
            # send the expression to evaluate
            child.sendline(":{\n%s\n:}\n" % self.expr)

            # collect the input echoed back by GHCi
            j = child.expect([":}[\r\n]*", pexpect.TIMEOUT])
            if j == 0:
                print ("Collected the echoed input.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                pass
            else:
                print ("FAILED to collect echoed input!\n\n\n\n")
                raise "ACK"

            # collect all the output.
            j = child.expect([self.prompt_re, pexpect.TIMEOUT])
            print ("Collecting the output.\n")
            print ("Before part:\n%s\n" % child.before.decode())
            print ("After part:\n%s\n" % child.after.decode())


            print ("\n\n\nShowing results of evaluation\n")
            print ("In directory: %s\n" % os.getcwd())
            print ("----------------------------------------------------------------------\n")
            print ("----------------------------------------------------------------------\n")

            if j == 0:
                print ("Evaluation completed, result is:\n")
                #print (str)
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                student_expr = indent( stripLast(child.before.decode()), 3)
                print ("\nStudent Expression as in report:\n%s\n" % student_expr)

                str = "   The value from your code is as follows:\n   ```\n"
                str += student_expr
                str += "\n   ```\n"
            else:
                print ("Evaluation failed for some reason.\n")                
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())
                str = "Evaluation failed.\n"

        else:
            print ("Loading the file failed.\n")                
            print ("Before part:\n%s\n" % str(child.before))
            print ("After part:\n%s\n" % str(child.after))
            str ="Loading the file failed.\n"

        have_score = False
        while not have_score:
            try:
                score = int(input("\n\nEnter number of points for %s (%d): " %
                                  (self.filename, self.possible)))
                have_score = True
            except:
                print("An invalid string was entered.  Try again.\n")

        comment = input("\nEnter a comment for this score: ")

        desc = self.description + "\n\n" + str + "\n\n" + comment

        return [ ResultReport(ResultType.testpass, score, self.possible, desc) ]

class HaskellEvalMsg(Test):
    '''Evaluate Haskell expression, for manual inspection and scoring later.'''

    def __init__(self,filename,possible,expr,match,description,timeout=5):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.match = match
        self.description = description
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('ghci', timeout=self.timeout)
        child.expect('GHCi, version 7.10.3')

        child.sendline(":l \"%s\"" % self.filename)
        i = child.expect(['Ok, modules loaded(.*)([\r\n]*)(.*)>', 'Failed,(.*\r\n)*#', 
                          pexpect.TIMEOUT])

        if i == 0:
            i = child.expect(['(.*)([\r\n]*)(.*)>', pexpect.TIMEOUT])

            child.sendline("%s" % self.expr)
            j = child.expect([self.match, pexpect.TIMEOUT])
            #str = child.readline()

            if j == 0:
                #str = "Before part:\n%s\n" % child.before.decode()
                #str += "After part:\n%s\n\n" % child.after.decode()
                str = "   The value from your code is as follows:\n   ```\n"
                str += indent( strip(child.after.decode()), 3)
                str += "\n   ```\n"
            else:
                str = "Evaluation failed.\n"
        else:
            str ="Loading the file failed.\n"

        desc = self.description
        desc += "\n\n"
        desc += str
        return [ ResultReport(ResultType.testpass, 0, self.possible, desc) ]

# Scheme specific tests
# --------------------------------------------------
class SchemeCheck(Test):
    '''Check for syntactic correctness of Scheme program.'''

    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check for syntactic correctness of Scheme program."
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('scheme', timeout=self.timeout)
        child.expect(re.escape('1 ]=> '))

        child.sendline("(load \"%s\")" % self.filename)
        child.expect(re.escape("(load \"%s\")\r\n\r\n" % self.filename))
        child.expect(";Loading \"%s\"\.\.\." % self.filename)
        i = child.expect([' done\r\n;Value: .*\r\n', ';To continue, call RESTART with an option number:', pexpect.TIMEOUT])

        if i == 0:
            desc  = self.description
            desc += "\n\n"
            desc += "     No syntax errors in \"%s\".\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += child.before.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class SchemeEvalEqualTest(Test):
    '''Check for that a scheme program evaluates to the given value.'''

    def __init__(self,filename,possible,expr,result,timeout=5,comment=""):
        self.filename = filename
        self.possible = possible
        self.expr = expr
        self.correct_result = result
        self.description = "Check that %s evaluates to `%s` (use `equal?` to check for equality).\n\n   %s" % (wrap(expr),result,comment)
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('scheme', timeout=self.timeout)
        child.expect(re.escape('1 ]=> '))

        child.sendline("(load \"%s\")" % self.filename)
        child.expect(re.escape("(load \"%s\")\r\n\r\n" % self.filename))
        child.expect(";Loading \"%s\"\.\.\." % self.filename)
        i = child.expect([' done\r\n;Value: .*\r\n', ';To continue, call RESTART with an option number:', pexpect.TIMEOUT])

        if i == 0:
            child.expect(re.escape('1 ]=> '))
            child.sendline('(equal? %s %s)' % (self.expr, self.correct_result))
            child.expect(re.escape('(equal? %s %s)\r\n\r\n' % (self.expr, self.correct_result)))
            j = child.expect([';Value: ', ";To continue, call RESTART with an option number:", pexpect.TIMEOUT])
            if j == 0:
                child.expect("\r\n")
                output = child.before.decode()
                if output == '#t':
                    return [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                          self.description + "\n\n") ]
                else:
                    return [ ResultReport(ResultType.testfail, self.possible, self.possible,
                                          self.description + "\n\n") ]
            elif j == 1:
                # Error in evaluation
                desc  = self.description + "\n\n"
                desc += "   Test failed. The following errors were reported:\n"
                desc += wrap(child.before.decode())
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

            else:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Test failed. A timeout (or other exception) occurred before "
                desc += "your code completed.  Please try the problem in your solution "
                desc += "and let Eric know if it does in fact work.\n"
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
                
                        
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += child.before.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \"%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

# Prolog specific tests
# --------------------------------------------------
class PrologCheck(Test):
    '''Check for compilation errors in a Prolog program.'''

    def __init__(self,filename,possible=3,timeout=5):
        self.filename = filename
        self.possible = possible
        self.description = "Check for compilation errors in a Prolog program."
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('swipl -q --nosignals -tty', timeout=self.timeout)
        #child.expect('Welcome to SWI-Prolog (Multi-threaded, 64 bits, Version 7.2.3)')
        #child.expect('(.|\r\n)*\?- ')

        child.sendline("[%s]." % self.filename.split('.')[0])
        i = child.expect(['true.', 'ERROR: [^\033]*', pexpect.TIMEOUT])

        if i == 0:
            desc  = self.description
            desc += "\n\n"
            desc += "     No compilation errors in \"%s\".\n\n" % self.filename
            return [ ResultReport(ResultType.testpass, self.possible, self.possible, desc) ]
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\".\n\n" % self.filename
            desc += "```\n"
            desc += child.after.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class PrologSingleQuery(Test):
    '''Evaluate a prolog query and check if the first result is correct'''

    def __init__(self,filename,possible,query,result,timeout=5):
        self.filename = filename
        self.possible = possible
        self.query = query
        self.correct_result = result
        self.description = "Check that %s is satisfied by `%s`.\n" % (wrap(query),result)
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('swipl -q --nosignals -tty', timeout=self.timeout)
        #child.expect('Welcome to SWI-Prolog (Multi-threaded, 64 bits, Version 7.2.3)')
        #child.expect('(.|\r\n)*\?- ')

        child.sendline("[%s]." % self.filename.split('.')[0])
        i = child.expect(['true.', 'ERROR: .*', pexpect.TIMEOUT])

        if i == 0:
            child.expect('[0-9]* \?- ')
            # send the query to evaluate
            child.sendline("%s.\r\n" % self.query)
            child.expect('%s' % re.escape(self.query))
            #child.expect('(\033\[C)*')

            j = child.expect(['[0-9]* \?- ', 'ERROR: .*', pexpect.TIMEOUT])

            if j == 0:
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                # Strip newlines and carrage returns
                stripped_output = output
                for char in "\r\n":
                    stripped_output = stripped_output.replace(char, "")

                if self.correct_result in stripped_output:
                    # It worked.
                    return [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                          self.description + "\n\n") ]

                else:
                    # It didn't - just show results.
                    desc  = self.description + "\n\n"
                    desc += "   Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            elif j == 1:
                desc  = self.description
                desc += "\n\n"
                desc += "   An error occured while evaluating your solution\n\n"
                desc += "```\n"
                desc += child.match.group(0).decode()
                desc += "\n```\n"
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            else:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Your solution took to long to run.  Check that it will always terminate? "
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\".\n\n" % self.filename
            desc += "```\n"
            desc += child.after.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

class PrologMultipleQuery(Test):
    '''Evaluate a prolog query and check if the results are correct'''

    def __init__(self,filename,possible,query,results,timeout=5):
        self.filename = filename
        self.possible = possible
        self.query = query
        self.correct_results = results
        self.description = "Check that %s is satisfied by `%s`.\n" % (wrap(query),'; '.join(results))
        self.timeout=timeout

    def run(self):
        child = pexpect.spawn('swipl -q --nosignals -tty', timeout=self.timeout)
        #child.expect('Welcome to SWI-Prolog (Multi-threaded, 64 bits, Version 7.2.3)')
        #child.expect('(.|\r\n)*\?- ')

        child.sendline("set_prolog_flag(color_term, false).")
        child.sendline("[%s]." % self.filename.split('.')[0])
        i = child.expect(['true.', 'ERROR: .*', pexpect.TIMEOUT])

        if i == 0:
            child.expect('[0-9]* \?- ')
            # send the query to evaluate
            child.sendline("%s; false." % self.query)
            for res in self.correct_results:
                child.sendline(";")
            child.expect('%s; false\.' % re.escape(self.query))
            #child.expect('(\033\[C)*')

            j = child.expect(['[0-9]* \?- ', 'ERROR: .*', pexpect.TIMEOUT])

            if j == 0:
                output = child.before.decode()
                print ("Collecting the output.\n")
                print ("Before part:\n%s\n" % child.before.decode())
                print ("After part:\n%s\n" % child.after.decode())

                # Strip newlines and carrage returns
                stripped_output = output
                for char in "\r\n":
                    stripped_output = stripped_output.replace(char, "")

                passed = True
                for res in self.correct_results + ['false.']:
                    passed &= res in stripped_output

                if passed:
                    # It worked.
                    return [ ResultReport(ResultType.testpass, self.possible, self.possible,
                                          self.description + "\n\n") ]

                else:
                    # It didn't - just show results.
                    desc  = self.description + "\n\n"
                    desc += "   Your solution evaluated (incorrectly) to some part of the following: "
                    desc += wrap(output) + "\n"
                    return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            elif j == 1:
                desc  = self.description
                desc += "\n\n"
                desc += "   An error occured while evaluating your solution\n\n"
                desc += "```\n"
                desc += child.match.group(0).decode()
                desc += "\n```\n"
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            else:
                # Timeout
                desc  = self.description + "\n\n"
                desc += "   Your solution took to long to run.  Check that it will always terminate? "
                return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
            
        elif i == 1:
            desc  = self.description
            desc += "\n\n"
            desc += "     Errors were found in \"%s\".\n\n" % self.filename
            desc += "```\n"
            desc += child.after.decode()
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]
        else:
            desc  = self.description
            desc += "\n\n"
            desc += "     Unexpected error #1, timeout on child.expect for \".%s\"\n\n" % self.filename
            desc += "```\n"
            desc += str(child.after)
            desc += "\n```\n"
            return [ ResultReport(ResultType.testfail, 0, self.possible, desc) ]

# Tests that just print a message
# --------------------------------------------------
class Message(Test):
    def __init__(self, msg):
        self.description = msg
        self.msg = msg

    def run(self):
        return [ MsgReport(self.msg) ]

    def not_run_desc(self):
        return [ MsgReport(self.msg) ]

class TimestampMessage(Test):
    def __init__(self):
        self.description = "Timestamp"
        #self.msg = ""

    def run(self):
        current_date = datetime.datetime.now()
        timestamp = current_date.strftime("%B %d, %H:%M:%S %p")
        msg = "Run on %s." % timestamp
        return [ MsgReport(msg) ]

    def not_run_desc(self):
        current_date = datetime.datetime.now()
        timestamp = current_date.strftime("%B %d, %H:%M:%S %p")
        msg = "Scheduled to run on %s." % timestamp
        return [ MsgReport(msg) ]
        

# show test results
# --------------------------------------------------


def showResult(forAssessment:bool) -> str:
    '''Convert a test result into a Markdown string.'''
    return lambda r : r.show(forAssessment)


def sumScores (r1, r2):
    #return ((r1.score + r2.score), (r1.possible + r2.possible))
    return r1.score + r2.score

def updateTotal (res, score, possible):
    #if isinstance(a, dict):
    #do_something()
    #res.score = score
    #res.possible = possible
    pass 

def showResults(results, forAssessment:bool) -> str :
    '''Convert a list of test results into a Markdown string.'''
    #sc = reduce(lambda r1, r2: r1.score + r2.score , results)
    #updateTotal(results, score, possible)
    reslist = map(showResult(forAssessment), results)
    return "".join(reslist)


def computeTotals(results):
    totalScore = 0
    totalPossible = 0
    for r in results:
        totalScore += r.score
        totalPossible += r.possible

    return (totalScore,totalPossible)

def computeTotalScore(results):
    (totalScore, totalPossible) = computeTotals(results)
    for r in results:
        if isinstance(r, TotalScoreReport):
            print ("...Total score: %s, total possible %s\n" % (str(totalScore), str(totalPossible)))
            r.score = totalScore
            r.possible = totalPossible




# create CSV data
# --------------------------------------------------
def csvResults(results, uiid):
    '''Convert a list of test results into a CSV string.'''


    res = uiid
    for r in results:
        if r.reportScore:
            res += ",%d" % r.score

    return res + "\n"
