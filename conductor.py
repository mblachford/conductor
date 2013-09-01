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
import src.util.vcenter as vcsa
import src.util.parser as data_parser
import src.util.mob as mob


def Parse(input,env):
    '''parse data provided and return values'''
    data = data_parser.parse(input,env)
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
    parser.add_argument('-c', action='store', dest='component', choices=['zombie', 'vshield', 'netsvcs'], \
                        help='yaml configuration file to pull data from', required=True)
    args = parser.parse_args()
    passwd=getpass.getpass("password for {} on {}:".format(args.username,args.target))

    raw_data = {}
    #connect to vcsa
    vcsa_cursor = Connect(args.target,args.username,passwd)

    #pull esxi data
    esx_info = mob.get_esx_env(vcsa_cursor.client)
    raw_data['ESX_INFO'] = esx_info

    #pull vm data
    vm_info = mob.poll_all_vms(vcsa_cursor.client)
    raw_data['VM_INFO'] = vm_info

    #ingest local data
    yaml_file = Parse(args.filename,args.component)
    raw_data['YAML_FILE'] = yaml_file

    to_add = Compare(raw_data)

    #disconnect from vcsa
    vcsa_cursor.disconnect()
