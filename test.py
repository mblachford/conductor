#!bin/python -B

import src.util.vcenter as vcsa
import src.util.mob as mob

handle = vcsa.Transport('10.6.28.66','root','m0n3yb0vin3')
vms = mob.poll_all_vms(handle.client)

for each in vms:
    print each.name,each.summary.guest.ipAddress


handle.disconnect()
