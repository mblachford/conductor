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
    parser.add_argument('-c', action='store', dest='component', choices=['zombie', 'vshield', 'netsvcs', 'other'], \
                        help='yaml configuration file to pull data from', required=True)
    args = parser.parse_args()
    passwd=getpass.getpass("Password for {} on {}:".format(args.username,args.target))
    print "\nStarting configuration pass on {}. Output logged to ~/log/conductor.log\n".format(args.target)

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
                vm_data.append("{},{}".format(each['name'],each['ip']))
            except:
                pass
        else:
            vm_data.append("{},{}".format(each['name'],each['ip']))
    global_data['VM'] = vm_data

    yaml_file = Parse(args.filename,args.component)
    global_data['YAML'] = yaml_file

    to_add = Compare(global_data)
    vcsa_cursor.clone(vcsa_cursor.client,to_add)
    
    vcsa_cursor.disconnect()
