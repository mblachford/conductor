import os
import logging

path = os.path.abspath(os.path.dirname(__file__)).rstrip('src')
logfile =('{0}/log/{1}'.format(path,'conductor.log'))

rootlogger = logging.getLogger()
loghdlr = logging.FileHandler(logfile)
time_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
loghdlr.setFormatter(time_formatter)
rootlogger.addHandler(loghdlr) 
rootlogger.setLevel(logging.INFO)
