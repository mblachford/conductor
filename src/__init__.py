import os
import logging

base = os.path.abspath(os.path.dirname(__file__)).rstrip('src')
logdir = ('{}/{}'.format(base,'log'))
logfile = ('{0}/log/{1}'.format(base,'conductor.log'))


if not os.path.isdir(logdir):
    os.mkdir(logdir,0755)
    open(logfile, 'w').close()
elif os.path.isdir(logdir):
    if os.path.exists(logfile):
        pass
    else:
        open(logfile, 'w').close()
        

logging.basicConfig(filename=logfile,
                    filemode='a',
                    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logging.getLogger('psphere').setLevel(logging.CRITICAL)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
