import datetime

def getTimeStamp():
    return str(datetime.datetime.today() )

def queryYesNo(question, default=None):
    """Ask a yes/no question via raw_input() and return the boolean equivalent"""
    
    valid = {"yes": True, "ye": True, "y": True, "yea": True, "yep": True, "ya": True,
            "no": False, "n": False, "nope": False, "nah": False, "nop": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: {0}".format(default))

    while True:
        print("{0} {1}".format(question, prompt))
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' \n")

def strip (lines):
    if lines[0] == chr(94):
        lines = lines[2:]

    return '\n'.join((lines.split('\n'))[2:-1])

def stripLast (lines):
    if lines[0] == chr(94):
        lines = lines[2:]

    return '\n'.join((lines.split('\n'))[:-1])

def indent(lines, amount, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))

def wrap(s):
    if len(s) == 0:
        return "` `"
    if s[0] == chr(94):
        s = s[2:]
    #tt = str(ord(s[0]))
    if s[0] == "\n" or s[0] == "\r":
        return "\n   ```%s   ```\n" % indent(s,4)
    elif len(s) > 80:
        return "\n   ```\n%s\n   ```\n" % s
    else:
        return "`%s`" % s

