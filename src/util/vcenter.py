import os
import sys
import logging
import psphere.client

log = logging.getLogger(__name__)

class Transport():

    def __init__(self, target, username, password):
        self.client = self.connect(target, username, password)

    def connect(self,target,username,password):
        ''' instantiate a connection to target instance '''
        try:
            log.info("Attempting to connect to vCenter {}".format(target))
            client = psphere.client.Client(target,username,password)
            log.info("Connected to vCenter {}".format(target))
            return client
        except Exception, e:
            log.info("Connection to vCenter {} failed. Reason: {}".format(target,e))

    def disconnect(self):
        ''' close connection to target instance '''
        try:
            log.info("Closing connection to vCenter")
            self.client.logout()
        except Exception, e:
            log.info("Failed to gracefully close the connection to vCenter. Reason: {}".format(e))

