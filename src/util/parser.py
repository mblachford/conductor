import logging
import yaml
from random import choice

log = logging.getLogger(__name__)

def parse(input,root,node):
    ''' base yaml parser module '''
    try:
        log.info("Parsing {} and building data tree".format(input))
        stream = open(input,'r')
        data = yaml.load(stream)
        refined = data[root][node]    
        return refined
    except Exception, e:
        log.info("Unable to parse {} and build the data tree. Reason: {}".format(input,e))

def compare(input):
    '''this is where we compare and build mapping values to put back into vCenter'''

    yaml_data = input['YAML']
    vm_data = input['VM']
    esx_data = input['ESX']

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
        _cluster = in_data['cluster']

        log.info("Comparing provided manifest to already installed virtual machines for entry {}".format(_name))

        if _name in vm_data:
            log.error("Found an already existing virtual machine with the name {}. Skipping installation".format(_name))
            pass
        elif not _name in vm_data:
            log.info("Unable to find a VM with the name {} in vCenter. Constructing paylod for provisioning".format(_name))
            _build['vm_name'] = _name
            _build['template'] = _template
            _build['ip'] = _ip
            _build['netmask'] = _netmask
            _build['gateway'] = _gateway
            _build['cores'] = _cores
            _build['cpus'] = _cpus
            _build['memory'] = _memory
            _build['vm_name'] = _name
            _build['dns'] = _dns_srv
            _build['domain'] = _domain
            _build['cluster'] = _cluster
            payload.append(_build)
    return payload
