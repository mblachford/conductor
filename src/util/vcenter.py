import os
import sys
import time
import logging
from string import Template
from random import choice
import psphere.client as vcsa_client
from psphere.managedobjects import ClusterComputeResource
from psphere.managedobjects import VirtualMachine
from psphere.managedobjects import HostSystem
from psphere.managedobjects import ResourcePool
from psphere.managedobjects import Task
from psphere.soap import VimFault

log = logging.getLogger(__name__)

class Transport():

    def __init__(self, target, username, password):
        self.client = self.connect(target, username, password)

    def connect(self,target,username,password,wsdl_location='remote'):
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
            try:
                cluster = ClusterComputeResource.get(cursor, name=data['cluster'])
            except Exception, e:
                log.error("Unable to locate a cluster resource witht the name {}. Omitting build".format(data['cluster']))
            else:
                pool = cluster.resourcePool
                esxhost = choice(cluster.host)
                datastore = choice(cluster.datastore)
                log.info("Cloning virtual machine named {} into cluster {} from template {}".format(data['vm_name'],data['cluster'],data['template']))
                template = VirtualMachine.get(cursor, name=data['template'])
                folder = cluster.parent.parent.vmFolder

                _ip_spec = self._vm_ip_spec(cursor, domain = data['domain'],
                                            dns = data['dns'],
                                            gateway = data['gateway'],
                                            ip = data['ip'],
                                            netmask = data['netmask'])
                _adapter_spec = self._vm_adapter_spec(cursor,_ip_spec)
                _net_spec = self._vm_net_spec(cursor,cluster.network, vlan = data['vlan'])
                _custom_spec = self._vm_custom_spec(cursor, _adapter_spec, template = data['template'],
                                                    domain = data['domain'], name = data['vm_name'],
                                                    ip = data['ip'], gateway = data['gateway'],
                                                    netmask = data['netmask'], dns = data['dns'])
                _config_spec = self._vm_config_spec(cursor, _net_spec, memory = data['memory'], 
                                                    cpus = data['cpus'], cores = data['cores'],
                                                    name = data['vm_name'])
                _relo_spec = self._vm_relo_spec(cursor,esxhost,datastore,pool)
                _clone_spec = self._vm_clone_spec(cursor, _relo_spec, _config_spec, _custom_spec)

                try:
                    #self.wait_for_task(template.CloneVM_Task(folder = folder, name = data['vm_name'], spec=_clone_spec))
                    template.CloneVM_Task(folder = folder, name = data['vm_name'], spec=_clone_spec)
                except VimFault, e:
                    print e

    def _vm_config_spec(self,cursor,net_spec,**kwargs):
        config_spec = cursor.create("VirtualMachineConfigSpec")
        config_spec.memoryMB = kwargs['memory']
        config_spec.numCPUs = kwargs['cpus']
        config_spec.name = kwargs['name']
        if not net_spec == None:
            config_spec.deviceChange = net_spec
        else:
            pass
        #config_spec.numCoresPerSocket = kwargs['cores']
        return config_spec

    def _vm_ip_spec(self,cursor,**kwargs):
        ip_spec = cursor.create("CustomizationIPSettings")
        fixed_ip = cursor.create("CustomizationFixedIp")
        fixed_ip.ipAddress = kwargs['ip']
        ip_spec.dnsDomain = kwargs['domain']
        ip_spec.dnsServerList = kwargs['dns']
        ip_spec.gateway = kwargs['gateway']
        ip_spec.ip = fixed_ip
        ip_spec.subnetMask = kwargs['netmask']
        ip_spec.netBIOS = None
        return ip_spec

    def _vm_net_spec(self,cursor,netinfo,**kwargs):
        for network in netinfo:
            if network.name == kwargs["vlan"]:
                log.info("Customizing VM network configuration for vlan {}.".format(kwargs['vlan']))
                net = network
                ds_conn = cursor.create("DistributedVirtualSwitchPortConnection")
                ds_conn.portgroupKey = net.key
                ds_conn.switchUuid = "{}".format(net.config.distributedVirtualSwitch.uuid)

                backing = cursor.create("VirtualEthernetCardDistributedVirtualPortBackingInfo")
                backing.port = ds_conn

                connect_info = cursor.create("VirtualDeviceConnectInfo")
                connect_info.allowGuestControl = True
                connect_info.connected = True
                connect_info.startConnected = True

                nic = cursor.create("VirtualVmxnet3") 
                nic.backing = backing
                nic.key = 4000
                nic.unitNumber = 0
                nic.addressType = "generated"
                nic.connectable = connect_info

                net_spec = cursor.create("VirtualDeviceConfigSpec")
                net_spec.device = nic
                net_spec.fileOperation = None
                operation = cursor.create("VirtualDeviceConfigSpecOperation")
                net_spec.operation = (operation.add)

                return net_spec
            else:
                pass

        log.error("Unable to find the network named {}. Continuing with out formal network specifciation".format(kwargs['vlan']))
        net_spec = None
        return net_spec


    def _vm_adapter_spec(self,cursor,ip_spec):
        nic_config = cursor.create("CustomizationAdapterMapping")
        nic_config.adapter = ip_spec
        return nic_config

    def _vm_custom_spec(self,cursor,adapter_spec,**kwargs):
        custom_spec = cursor.create("CustomizationSpec")
        host_name = cursor.create("CustomizationFixedName")
        host_name.name = kwargs['name']
        ip_spec = cursor.create("CustomizationGlobalIPSettings")
        ip_spec.dnsServerList = kwargs['dns']
        ip_spec.dnsSuffixList = kwargs['domain']

        if 'windows' in kwargs['template'].lower():
            log.info("Calling windows customization specification")
            sysprep = self._gen_sysprep(**kwargs)
            identity_spec = cursor.create("CustomizationSysprepText")
            identity_spec.value = sysprep
        else:
            log.info("Calling Linux customization specification")
            identity_spec = cursor.create("CustomizationLinuxPrep")
            identity_spec.domain = kwargs['domain']
            identity_spec.hostName = host_name
            identity_spec.hwClockUTC = True

        custom_spec.globalIPSettings = ip_spec
        custom_spec.identity = identity_spec
        custom_spec.nicSettingMap = adapter_spec
        return custom_spec

    def _vm_relo_spec(self,cursor,host,disk,pool):
        relo_spec = cursor.create("VirtualMachineRelocateSpec")
        relo_spec.host = host
        relo_spec.datastore = disk
        relo_spec.transform = "sparse"
        relo_spec.pool = pool
        return relo_spec

    def _vm_clone_spec(self,cursor,relo_spec, config_spec, custom_spec):
        clone_spec = cursor.create("VirtualMachineCloneSpec")
        clone_spec.config = config_spec
        clone_spec.customization = custom_spec
        clone_spec.location = relo_spec
        clone_spec.powerOn = True
        clone_spec.snapshot = None
        clone_spec.template = False
        return clone_spec

    def _gen_sysprep(self,**kwargs):
        ''' modify the sysprep file '''
        dir = os.path.abspath(os.path.dirname(__file__))
        raw_file = open('{}/.unattend.xml'.format(dir)).read()
        mod = Template(raw_file)  
        if len(kwargs['name']) > 15:
            hname = kwargs['name'][0:15]
        else: 
            hname = kwargs['name']
        sysprep = mod.substitute(name = hname,
                                 gateway = kwargs['gateway'],
                                 ip = kwargs['ip'],
                                 cidr = '26',
                                 dns1 = kwargs['dns'].split(',')[0],
                                 dns2 = kwargs['dns'].split(',')[1])
        return sysprep

    def wait_for_task(self,task):
        if isinstance(task, Task):
            while task.info.state in ["queued", "running"]:
                time.sleep(1)
                task.update()
            if task.info.state == "success":
                return True
            else:
                log.warn("Task failed: {0}".format(task.info))
                return False
        else:
            log.warning("Passed non task object into wait_for_task")
            return False
