import os
import sys
import logging
import psphere.managedobjects as vcsa_objects

log = logging.getLogger(__name__)


def poll_all_vms(cursor):
    ''' mine our connection on the target instance for objects'''
    try:
        log.info("Attempting to poll all virtual machine objects")
        data = vcsa_objects.VirtualMachine.all(cursor)
        return data
    except Exception, e:
        log.info("Polling VM objects from vCenter failed. Reason: {}".format(e))
