#!bin/python -B

import src.util.vcenter as vcsa
import src.util.mob as mob

handle = vcsa.Transport('','','')
vms = mob.poll_all_vms(handle.client)

for each in vms:
    print each.name,each.summary.guest.ipAddress


handle.disconnect()
