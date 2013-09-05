import logging
import yaml
from random import choice

log = logging.getLogger(__name__)

def parse(input,*args):
    ''' base yaml parser module '''
    if len(args) > 0:
        yaml_node = args[0]
    else:
        pass
    try:
        log.info("Parsing {} and building data tree".format(input))
        stream = open(input,'r')
        data = yaml.load(stream)
        refined = data[yaml_node]    
        return refined
    except Exception, e:
        log.info("Unable to parse {} and build the data tree".format(input))

def compare(input):
    '''this is where we compare and build mapping values to put back into vCenter'''

    yaml_data = input['YAML']
    vm_data = input['VM']
    esx_data = input['ESX']

    phys = choice(esx_data).split(',')
    host = phys.pop(0)
    datastore = choice(phys)

    payload = []
    while yaml_data:
        _build = {}
        in_data = yaml_data.pop(0)
        _template = in_data['template']
        _name = in_data['name']
        _ip = in_data['ip']
        _netmask = in_data['netmask']
        _gateway = in_data['gateway']
        _cores = in_data['cores']
        _cpus = in_data['cpus']
        _memory = in_data['memory']
        _domain = in_data['domain']
        _dns_srv = in_data['dns_servers']

        log.info("Comparing provided manifest to already installed virtual machines for entry {}".format(_name))

        for raw_data in vm_data:
            if _name in raw_data and _ip in raw_data:
                log.error("Found an already existing virtual machine with the name {} and ip address {}. Skipping installation".format(_name,_ip))
                break
            elif not _name in raw_data or not _ip in raw_data:
                log.info("Unable to locate a VM in inventory with the name {} and an IP of {}. Safe to build. Generating payload for delivery".format(_name,_ip))
                _build['vm_name'] = _name
                _build['template'] = _template
                _build['ip'] = _ip
                _build['netmask'] = _netmask
                _build['gateway'] = _gateway
                _build['cores'] = _cores
                _build['cpus'] = _cpus
                _build['memory'] = _memory
                _build['vm_name'] = _name
                _build['esx_host'] = host
                _build['datastore'] = datastore
                _build['dns'] = _dns_srv
                _build['domain'] = _domain
        payload.append(_build)
    return payload
