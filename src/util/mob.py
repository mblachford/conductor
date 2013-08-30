import os
import sys
import logging
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
        return data
    except Exception, e:
        log.info("Polling VM objects from vCenter failed. Reason: {}".format(e))

def poll_single_vm(cursor,vmname):
    ''' mine our connection on the target instance for objects'''
    try:
        log.info("Attempting to poll vCenter for virtual machine object: {}".format(vmname))
        data = vcsa_objects.VirtualMachine.get(cursor, name='{}'.format(vmname))
        print data
        return data
    except Exception, e:
        log.info("Polling for virtual machine object {} failed. Reason: {}".format(vmname,e))

def clone_template(cursor,template_name,values):
    ''' clone our souce template to a virutal machine with the 
        provided specifications:
          VirtualMachineConfigSpec - changes to virtual hardware
          CustomizationSpec - guest os customization
          VirtualMachineRelocateSpec - cloned VM destination information
    '''
    vm_config_spec = client.create("VirtualMachineConfigSpec")

    vm_clone_spec = client.create("VirtualMachineCloneSpec")
    vm_clone_spec.powerOn = True
    vm_clone_spec.template = False
    vm_clone_spec.location = vm_reloc_spec

    vm_reloc_spec = client.create("VirtualMachineRelocateSpec")
    vm_reloc_spec.datastore = vm.datastore
    vm_reloc_spec.pool = vm.resourcePool
    vm_reloc_spec.host = host_system

    vm = cursor.VirtualMachine.get(client, name=template_name)
    name = options.vmname
    folder = vm.parent.parent.vmFolder # Datacenter folder

    try:
        cursor.CloneVM_Task(folder = folder, name = name, spec=vm_clone_spec)
    except VimFault, e:
        print("Failed to clone %s: " % e)
        sys.exit()
    client.logout()
