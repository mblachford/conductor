import logging
import yaml

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
    '''this is where we compare and build mapping values to put back into vCenter
       We need 3 things:
       vm info
       yaml file
       esx info
    '''

    yaml_data = input['YAML']
    vm_data = input['VM']
    esx_data = input['ESX']

    log.info("Comparing provided manifest to already installed virtual machines")
    for values in vm_data:
        host = values.split(',')[0]
        ip = values.split(',')[1]
        if HI == host and IP == ip:
            log.error("Found an already existing virtual machine with the name {} and ip address {}. Skipping installation".format(host,ip))
            break
        elif HI == host and not IP == ip:
            log.error("Found an already existing virtual machine with the name {} but an ip address of {}. Skipping installation".format(host,ip))
            break
        elif not HI == host and IP == ip:
            log.error("Found an already existing virtual machine with the ip {} and a name of {}, not {} as specified in the yaml file. Skipping installation".format(ip,host,HI))
            break
        else:
            if host == HI:
                log.info("Unable to locate a virtual machine with the host name or {} or the ip address {}. Continuing installation".format(host,ip))
            else:
                pass







