#!bin/python -B

'''
conductor 0.0.1
author: Mason Blachford
email: masonb@vmware.com
License: GPLv2
'''

import os
import sys
import psphere
import getpass
import argparse
import zc.lockfile as locker
import src.util.vcenter as vcsa
import src.util.parser as data_parser
import src.util.mob as mob

class Lock:

    def __init__(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        fname = ".{}".format(__file__.lstrip('./'))
        self.lfile = "{}/{}".format(dirname,fname)

    def grab(self):
        try:
            locker.LockFile(self.lfile)
        except locker.LockError, e:
            print "unable to obtain exclusive lock. Reason: {}".format(e)
            sys.exit(-1)
        
    def release(self):
        try:
            locker.LockFile.close(locker.LockFile(self.lfile))
        except locker.LockError, e:
            print "unable to gracefully release lock, forcing"
        finally:
            if os.path.exists(self.lfile):
                os.remove(self.lfile)


def Parse(input,**kwargs):
    '''parse data provided and return values'''
    root = kwargs['root']  
    node = kwargs['node']
    data = data_parser.parse(input,root,node)
    return data

def Compare(input):
    '''compare data provided and return values'''
    data = data_parser.compare(input)
    return data

def Connect(target,username,password):
    '''connect to vcenter'''
    handle = vcsa.Transport(target,username,password)
    return handle
    

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='target', help='vCenter IP address or name', required=True)
    parser.add_argument('-u', action='store', dest='username', help='username to connect to vCenter with', required=True)
    parser.add_argument('-f', action='store', dest='filename', help='yaml configuration file to pull data from', required=True)
    parser.add_argument('-e', action='store', dest='environment', choices=['tlm', 'oss'], help='either tlm or oss', required=True)
    parser.add_argument('-c', action='store', dest='component', choices=['zombie', 'vshield', 'netsvcs', 'other'], \
                        help='yaml configuration file to pull data from', required=True)
    args = parser.parse_args()
    passwd=getpass.getpass("\nPassword for {} on {}:".format(args.username,args.target))
    print "\nStarting configuration pass on {}. Output logged to ~/log/conductor.log\n".format(args.target)

    exlock = Lock()
    exlock.grab()
    vcsa_cursor = Connect(args.target,args.username,passwd)

    global_data = {}
    esx_data = []
    esx_info = mob.get_esx_env(vcsa_cursor.client)
    for each in esx_info:
        if isinstance(each, dict):
            try:
                if isinstance(each['datastores'], list):
                    esx_data.append("{},{}".format(each['host'],','.join(each['datastores'])))
            except:
                pass
        else:
            esxl_data.append("{},{}".format(each['host'],each['datastores']))
    global_data['ESX'] = esx_data
            
    vm_data = []
    vm_info = mob.poll_all_vms(vcsa_cursor.client)
    for each in vm_info:
        if isinstance(each, dict):
            try:
                vm_data.append(each['ip'])
                vm_data.append(each['name'])
            except:
                pass
        else:
            vm_data.append(each['ip'])
            vm_data.append(each['name'])
    global_data['VM'] = vm_data

    yaml_file = Parse(args.filename, root=args.environment, node=args.component)
    global_data['YAML'] = yaml_file

    to_add = Compare(global_data)

    vcsa_cursor.clone(vcsa_cursor.client,to_add)
    vcsa_cursor.disconnect()
    exlock.release()
