import os
import sys
import logging
import inspect
import psphere.managedobjects as vcsa_objects

log = logging.getLogger(__name__)

def get_esx_env(cursor):
    ''' define the physical map of our vCenter '''
    try:
        log.info("Attempting to poll all ESXi objects")
        data = vcsa_objects.HostSystem.all(cursor)
        esx_data = []
        for each in data: 
            host_data = {}
            for all in each.name:
                host_data['host'] = each.name
                datastores = []
                for x in each.datastore:
                    datastores.append(x.info.name)
            host_data['datastores'] = datastores
            esx_data.append(host_data)
        return esx_data 
    except Exception, e:
        log.info("Polling ESXi objects from vCenter failed. Reason: {}".format(e))

def poll_all_vms(cursor):
    ''' mine our connection on the target instance for objects'''
    try:
        log.info("Attempting to poll all virtual machine objects")
        data = vcsa_objects.VirtualMachine.all(cursor)
        vm_data = []
        for each in data:
            vms_data = {}
            try:
                vms_data['name'] = each.name
                vms_data['ip'] = each.summary.guest.ipAddress
            except AttributeError:
                pass
            vm_data.append(vms_data)
        return vm_data
    except Exception, e:
        log.info("Polling VM objects from vCenter failed. Reason: {}".format(e))

def get_cluster_names(cursor,cname):
    ''' need to find all the cluster names '''
    try:
        cluster = vcsa_objects.ClusterComputeResource.get(cursor, name=cname)
    except ObjectNotFoundError, e:
        log.info("Unable to find cluster. Reason: {}".format(e))
        sys.exit(0)
