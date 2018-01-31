
# Utility functions used by the WebHook server.

# Many of these are to extract data out of the payload of JSON
# text send by the HTTP POST sent by github.umn.edu to the
# WebHook sever.

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

