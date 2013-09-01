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
    '''this is where we compare and build mapping values to put back into vCenter'''
    yaml_data = input['YAML_FILE']
    esx_data = input['ESX_INFO']
    vm_data = input['VM_INFO']

    if isinstance(yaml_data, list):
        for range in len(yaml_data):
            print yaml_data[range]
        
    #if yaml_data.has_key('oss'):
    #    print "yes, its in the vm data file"
