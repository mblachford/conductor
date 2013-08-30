#!bin/python -B

import src.util.vcenter as vcsa
import src.util.mob as mob

handle = vcsa.Transport('10.6.28.66','root','m0n3yb0vin3')
#vms = mob.poll_all_vms(handle.client)
esx = mob.get_esx_env(handle.client)

print esx



handle.disconnect()
