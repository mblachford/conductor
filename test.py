#!bin/python -B

from psphere.client import Client
from psphere.soap import VimFault
from psphere.managedobjects import HostSystem
from psphere.managedobjects import VirtualMachine


client = Client(server='10.6.28.66', username='root', password='m0n3yb0vin3')
print('Successfully connected to %s' % client.server)
print(client.si.CurrentTime())

host_system = HostSystem.get(client, name='d2p3s1ch0srv1oss-esx4.prod.vpc.vmw')

vm = VirtualMachine.get(client, name='Centos6.4-2013-08-24')
name = 'mason_test'
folder = vm.parent.parent.parent.vmFolder # Datacenter folder
vm_clone_spec = client.create("VirtualMachineCloneSpec")
vm_reloc_spec = client.create("VirtualMachineRelocateSpec")
vm_reloc_spec.datastore = 'd2p3s0vnx0oss-lun5'
vm_reloc_spec.pool = 'd2p3oss'
vm_reloc_spec.host = 'd2p3s1ch0srv1oss-esx4.prod.vpc.vmw'
vm_reloc_spec.transform = None
vm_clone_spec.powerOn = True
vm_clone_spec.template = False
vm_clone_spec.location = vm_reloc_spec

try:
    vm.CloneVM_Task(folder = folder, name = name, spec=vm_clone_spec)
except VimFault, e:
    print("Failed to clone %s: " % e)
    sys.exit()
client.logout()
