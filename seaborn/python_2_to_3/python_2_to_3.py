import sys

if sys.version_info[0] == 3:
    xrange = range
    basestring = str
    unicode = str
    from io import StringIO
else:
    from StringIO import StringIO
