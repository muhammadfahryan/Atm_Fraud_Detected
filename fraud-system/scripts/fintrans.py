#!/usr/bin/python3

""" 
  The implementation of the synthetic financial transaction stream,
  used in the main script of gess.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2013-11-08
@status: init
"""
import sys
import os
import socket
import logging
import string
import datetime
import random
import uuid
import csv
import json
from time import sleep

DEBUG = False

TARGET_HOST = os.environ.get('TARGET_HOST')
if TARGET_HOST is None: 
  TARGET_HOST = "localhost"

GESS_UDP_PORT = os.environ.get('TARGET_UDP_PORT')
if GESS_UDP_PORT is None: 
  GESS_UDP_PORT = 6900

# defines delay (seconds) to inject between events
DELAY = os.environ.get('EVENT_DELAY')
if DELAY is None: 
  DELAY = 1.50
else:
  DELAY=float(DELAY)

SAMPLE_INTERVAL = 10

FRAUD_TICK_MIN = 5

FRAUD_TICK_MAX = 15

AMOUNTS = [50000, 100000,150000, 200000,250000, 300000,350000, 400000,40000, 500000, 1000000,1500000, 2000000, 2500000]


if DEBUG:
  FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
  logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
  FORMAT = '%(message)s'
  logging.basicConfig(level=logging.INFO, format=FORMAT)


class FinTransSource(object):

  def __init__(self, atm_loc_sources):
         self.send_port = GESS_UDP_PORT
         self.atm_loc = {}
         for atm_loc in atm_loc_sources:
           self._load_data(atm_loc)
  
  def _load_data(self, atm_loc_data_file):
    logging.info('Trying to parse ATM location data file %s' %(atm_loc_data_file))
    osm_atm_file = open(atm_loc_data_file, 'r')
    atm_counter = 0
    try:
      reader = csv.reader(osm_atm_file, delimiter=',')
      for row in reader:
        lat, lon, atm_label, address = row[1], row[0], row[2], row[3]
        atm_counter += 1
        self.atm_loc[str(atm_counter)] = lat, lon, atm_label, address
        logging.debug(' -> loaded ATM location %s, %s' %(lat, lon))
    finally:
      osm_atm_file.close()
      logging.debug(' -> loaded %d ATM locations in total.' %(atm_counter))
  
  def _create_fintran(self):
    rloc = random.choice(list(self.atm_loc.keys()))
    lat, lon, atm_label, address = self.atm_loc[rloc]
    fintran = {
      'timestamp' : str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z+0000")),
      'atm' : str(atm_label),
      'address' : str(address),
      'location' : {
        'lat' : float(str(lon)),
        'lon' : float(str(lat))
      },
      'amount' : random.choice(AMOUNTS),
      'account_id' : 'a' + str(random.randint(1, 1000)),
      'transaction_id' : str(uuid.uuid1())
    }
    logging.debug('Created financial transaction: %s' %fintran)
    return (fintran, sys.getsizeof(str(fintran)))

  def _create_fraudtran(self, fintran):
    rloc = random.choice(list(self.atm_loc.keys()))
    lat, lon, atm_label, address = self.atm_loc[rloc]
    fraudtran = {
        'timestamp': str((datetime.datetime.now() - datetime.timedelta(seconds=random.randint(60, 600))).strftime(
            "%Y-%m-%d %H:%M:%S %z+0000")),
        'atm': str(atm_label),
        'address': str(address),
        'location': {
            'lat': float(str(lon)),
            'lon': float(str(lat))
        },
        'amount': random.choice(AMOUNTS),
        'account_id': fintran['account_id'],
        'transaction_id': 'xxx' + str(fintran['transaction_id'])
    }
    logging.debug('Created fraudulent financial transaction: %s' % fraudtran)
    return (fraudtran, sys.getsizeof(str(fraudtran)))


  def _send_fintran(self, out_socket, fintran):
    out_socket.sendto(str(fintran).encode() + b'\n', (TARGET_HOST, self.send_port))
    logging.debug('Sent financial transaction: %s' % fintran)

    
  def dump_data(self):
    for k, v in self.atm_loc.iteritems():
      logging.info('ATM %s location: %s %s' %(k, v[0], v[1])) 
  
  def run(self):
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # use UDP
    start_time = datetime.datetime.now()
    num_fintrans = 0
    tp_fintrans = 0
    num_bytes = 0
    tp_bytes = 0
    ticks = 0 # ticks (virtual time basis for emits)
    fraud_tick = random.randint(FRAUD_TICK_MIN, FRAUD_TICK_MAX) 

    logging.info('gess is now running!')
    logging.info('\nEvents are emitted with a delay of %s \non UDP to %s on port %s\nConsume them with a tool such as netcat, e.g.\n\tnc -v -u -l %s\n\n' % (DELAY,TARGET_HOST,GESS_UDP_PORT,GESS_UDP_PORT))
    logging.info('timestamp\t\ttxn\ttxn/s')
    
    while True:
      
      ticks += 1      
      logging.debug('TICKS: %d' %ticks)

      (fintran, fintransize) = self._create_fintran()
      self._send_fintran(out_socket, json.dumps(fintran))

      sleep(DELAY)

      if ticks > fraud_tick:
        (fraudtran, fraudtransize) = self._create_fraudtran(fintran)
        self._send_fintran(out_socket, json.dumps(fraudtran))
        num_fintrans += 2
        num_bytes += fintransize + fraudtransize
        ticks = 0
        fraud_tick = random.randint(FRAUD_TICK_MIN, FRAUD_TICK_MAX)
      else:  
        num_fintrans += 1
        num_bytes += fintransize
  
      end_time = datetime.datetime.now()
      diff_time = end_time - start_time
    
      if diff_time.seconds > (SAMPLE_INTERVAL - 1):
        tp_fintrans = (num_fintrans) / diff_time.seconds
        tp_bytes = (num_bytes/1024/1024) / diff_time.seconds
        logging.info('%s\t%d\t%d'
          %(
            str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
            (num_fintrans), 
            tp_fintrans
          )
        )
        start_time = datetime.datetime.now()
        num_fintrans = 0
        num_bytes = 0
