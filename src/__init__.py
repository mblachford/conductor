import os
import logging

path = os.path.abspath(os.path.dirname(__file__)).rstrip('src')
logfile =('{0}/log/{1}'.format(path,'conductor.log'))

logging.basicConfig(filename=logfile,
                    filemode='a',
                    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

#rootlogger = logging.getLogger()
#loghdlr = logging.FileHandler(logfile)
#time_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
#loghdlr.setFormatter(time_formatter)
#rootlogger.addHandler(loghdlr) 
#rootlogger.setLevel(logging.INFO)
