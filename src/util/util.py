import os
import sys
import logging
import inspect
import lockfile

log = logging.getLogger(__name__)

def acquire_lock():
    ''' lock _main_ from use '''
    try:
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        print mod.__name__
    except Exception, e:
        print "error: {}".format(e)
