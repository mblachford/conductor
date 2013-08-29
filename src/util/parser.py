import logging
import yaml

log = logging.getLogger(__name__)

def parse(input):
    try:
        log.info("Parsing {} and building data tree".format(input))
        stream = open(input,'r')
        value = yaml.load(stream)
        return value
    except Exception, e:
        log.info("Unable to parse {} and build the data tree".format(input))
