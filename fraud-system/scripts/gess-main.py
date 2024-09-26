#!/usr/bin/python3

""" 
  The main script of gess, the generator for synthetic streams 
  of financial transactions.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2013-11-07
@status: init
"""
import logging
import os
import time
from fintrans import FinTransSource

DEBUG = False
CONFIG_FILE = 'gess.conf'

if DEBUG:
    FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
    FORMAT = '%(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

def read_config():
    atm_loc_sources = []
    cf = os.path.abspath(CONFIG_FILE)
    if os.path.exists(cf):
        logging.info('Using config file %s, parsing ATM location sources to be used' % cf)
        with open(CONFIG_FILE, 'r') as file:
            lines = file.readlines()
            for line in lines:
                l = line.strip()
                if l and not l.startswith('#'):  # non-empty or non-comment line
                    atm_loc_source = os.path.abspath(l)
                    atm_loc_sources.append(atm_loc_source)
                    logging.debug(' -> added %s as a source' % atm_loc_source)
    else:
        logging.info('No gess config file found, using default source (C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/fraud-system/data/atm.csv)')
        atm_loc_source = os.path.abspath('C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/fraud-system/data/atm.csv')
        atm_loc_sources.append(atm_loc_source)
    return atm_loc_sources




if __name__ == '__main__':
    fns = FinTransSource(read_config())
    fns.run()
