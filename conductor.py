#!/usr/bin/env python

'''
conductor 0.0.1
author: Mason Blachford
email: masonb@vmware.com
License: GPL
'''
import os
import sys
import logger
import psphere
import getpass
import argparse
import logging
import src.util.vcenter as vcsa
import src.util.parser as data_parser

def ParseData(input):
    '''parse data provided and return values'''
    data = data_parser.parse(input)







if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='target', help='vCenter IP address or name', required=True)
    parser.add_argument('-u', action='store', dest='username', help='username to connect to vCenter with', required=True)
    parser.add_argument('-f', action='store', dest='filename', help='yaml configuration file to pull data from', required=True)
    parser.add_argument('-c', action='store', dest='component', choices=['zombie', 'vshield', 'netsvcs'], \
                        help='yaml configuration file to pull data from', required=True)
    args = parser.parse_args()

    passwd=getpass.getpass("password for {} on {}:".format(args.username,args.target))

    #ParseData(args.filename)
