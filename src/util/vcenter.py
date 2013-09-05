import os
import sys
import logging
import psphere.client as vcsa_client
from psphere.managedobjects import VirtualMachine
from psphere.managedobjects import HostSystem
from psphere.managedobjects import ResourcePool
from psphere.soap import VimFault

log = logging.getLogger(__name__)

class Transport():

    def __init__(self, target, username, password):
        self.client = self.connect(target, username, password)

    def connect(self,target,username,password):
        ''' instantiate a connection to target instance '''
        try:
            log.info("Attempting to connect to vCenter {}".format(target))
            client = vcsa_client.Client(target,username,password)
            log.info("Connected to vCenter {}".format(target))
            return client
        except Exception, e:
            log.error("Connection to vCenter {} failed. Reason: {}".format(target,e))
            sys.exit(1)

    def disconnect(self):
        ''' close connection to target instance '''
        try:
            log.info("Closing connection to vCenter")
            self.client.logout()
        except Exception, e:
            log.info("Failed to gracefully close the connection to vCenter. Reason: {}".format(e))
            sys.exit(1)

    def clone(self,cursor,payload):
        ''' clone the template with our payload '''
   
        while payload:
            data = payload.pop(0)
            template_name = data['template']
            log.info("Building virtual machine named {} from template {}".format(data['vm_name'],template_name))
            template = VirtualMachine.get(cursor, name=template_name)
            esxhost = HostSystem.get(cursor, name=data['esx_host'])
            #pool = ResourcePool.get(cursor)
            pool = 'd2p3oss'
            #folder = cursor.si.content.rootFolder
            folder = 'Management'

            #_config_spec = self._vm_config_spec(cursor,memory = data['memory'], cpus = data['cpus'])
           # _ip_spec = self._vm_ip_spec(cursor, domain = data['domain'], dns = data['dns'], gateway = data['gateway'], ip = data['ip'], netmask = data['netmask'])
           # _custom_spec = self._vm_custom_spec(cursor, _ip_spec)
            _relo_spec = self._vm_relo_spec(cursor, data['datastore'], esxhost.name, pool)
            _clone_spec = self._vm_clone_spec(cursor, _relo_spec)

            try:
                template.CloneVM_Task(folder = folder, name = data['vm_name'], spec=_clone_spec)
            except VimFault, e:
                print e

    def _vm_config_spec(self,cursor,**kwargs):
        config_spec = cursor.create("VirtualMachineConfigSpec")
        config_spec.memoryMB = kwargs['memory']
        config_spec.numCPUs = kwargs['cpus']
        #config_spec.numCoresPerSocket = args['cores']
        return config_spec

    def _vm_custom_spec(self,cursor,ipsettings):
        custom_spec = cursor.create("CustomizationSpec")
        custom_spec.globalIPSettings = ipsettings
        return custom_spec

    def _vm_ip_spec(self,cursor,**kwargs):
        ip_spec = cursor.create("CustomizationIPSettings")
        ip_spec.dnsDomain = kwargs['domain']
        ip_spec.dnsServerList = kwargs['dns']
        ip_spec.gateway = kwargs['gateway']
        ip_spec.ip = kwargs['ip']
        ip_spec.subnetMask = kwargs['netmask']
        ip_spec.netBIOS = None
        return ip_spec

    def _vm_relo_spec(self,cursor,disk,esxhost,pool):
        relo_spec = cursor.create("VirtualMachineRelocateSpec")
        #relo_spec.datastore = disk
        #relo_spec.host = esxhost
        relo_spec.transform = 'sparse'
        relo_spec.pool = pool
        return relo_spec

    def _vm_clone_spec(self,cursor,relo_spec):
        clone_spec = cursor.create("VirtualMachineCloneSpec")
        clone_spec.config = None
        clone_spec.customization = None
        clone_spec.location = relo_spec
        clone_spec.powerOn = False
        clone_spec.snapshot = None
        clone_spec.template = False
        return clone_spec
