import os
import sys
import logging
from pysqlite2 import dbapi2 as sqlite

log = logging.getLogger(__name__)

class Database():

    def __init__(self):
        self.connection = self.open()

    def open(self):
        ''' build our database and fetch a cursor '''
        try:
            log.info("Constructing in memory database")
            connection = sqlite.connect(':memory:')
            return connection
        except sqlite.Error, e: 
            log.error("Unable to construct the in memory database. Reason: {}".format(e))

    def frame(self,conn):
        ''' build our table space '''
        cursor = conn.cursor()
        tables = {'vms':'CREATE TABLE vm(vm_name TEXT, vm_ip TEXT PRIMARY KEY)',
                  'esx':'CREATE TABLE esx(name TEXT PRIMARY KEY, datastore TEXT)'}
        try:
            log.info("Populating in memory database schema ")
            for key,value in tables.iteritems():
                cursor.execute("""{}""".format(value))
                conn.commit()
            return
        except sqlite.Error, e:
            log.error("Unable to frame the database. Reason: {}".format(e))

    def insert(self,cursor, **kwargs):
        ''' build our table space '''
        pass


    def close(self, cursor):
        ''' close the connection to the database '''
        try:
            log.info("Closing connection to the database")
            cursor.close()
        except sqlite.Error, e:
            log.error("Unknown issue closing connection to the database. Killing with prejudice.")
