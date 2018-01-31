import os, os.path, string

os.environ['MODULESHOME'] = '/usr/local/modules-tcl'

if 'TCLSH' in os.environ:
   TCLSH=os.environ['TCLSH']
elif os.path.exists('/usr/bin/tclsh'):
    TCLSH="/usr/bin/tclsh"
elif os.path.exists('/bin/tclsh') :
   TCLSH="/bin/tclsh"
else: 
   TCLSH=""

if not 'MODULEPATH' in os.environ:
   os.environ['MODULEPATH'] = '/mips/tools/freeware/modulefiles'

if not 'LOADEDMODULES' in os.environ:
   os.environ['LOADEDMODULES'] = '';

def module(command, *arguments):
   if os.path.isfile('/usr/local/modules-tcl/modulecmd.tcl'):
      commands = os.popen('$TCLSH /usr/local/modules-tcl/modulecmd.tcl python %s %s' % (command, ' '.join(arguments))).read()
      exec(commands)
