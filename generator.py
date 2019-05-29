#!/usr/bin/env python3

import os
import logging
import json
import sqlite3
from time import sleep

import requests
import selenium.webdriver as webdriver

from zones import zones


class rublacklist:
  db_file_name = 'rublacklist.db'


  def get_blocked_json(self):
    try:
      url = 'https://api.reserve-rbl.ru/api/v2/current/json'
      return requests.get(url).json()
    except:
      with open('expand.txt') as f:
        return json.loads(
          f.read()
        )

  def expand(self, template):
    data = self.get_blocked_json()
    key = list(data.keys())[0]
    logging.debug('Founded key: {}'.format(key))
    ips = []
    for i in data[key]:
      for ip in i['ip']:
        logging.debug('Collected line: {}'.format(ip))
        ips.append(ip)
    for ip in ips:
      ip, prefix = subnet().get_prefix('103.246.200.0/22')
      logging.debug('Detected ip: {} with subnet: {}'.format(ip, prefix))
      template += 'push "route {} {}"\n'.format(ip, prefix)
    return template

  def db_open(self):
    logging.info('Invoked db_open')
    self.db = sqlite3.Connection(self.db_file_name)
    try:
      self.db.execute('CREATE TABLE cache (ip, subnet)')
      self.db.commit()
      logging.debug('Created table ...')
    except sqlite3.OperationalError:
      pass

  def db_close(self):
    logging.debug('Closing db ...')
    self.db.commit()
    self.db.close()
    logging.debug('Success')

  def create_cache(self):
    logging.info('Invoked create_cache')
    self.db_open()
    data = self.get_blocked_json()
    key = list(data.keys())[0]
    ips = []
    for i in data[key]:
      for ip in i['ip']:
#         logging.debug('Collected line: {}'.format(ip))
        ips.append(ip)
    for ip in ips:
      ip, prefix = subnets().get_prefix(ip)
#       if prefix == '255.255.255.255': continue
      self.db.execute(
        "INSERT INTO cache (ip, subnet) values ('{}', '{}')".format(ip, prefix)
      )
    self.db.execute(
      "DELETE FROM cache WHERE subnet == '255.255.255.255';"
    )
    self.db_close()

  def expand_from_cache(self, template):
    self.db_open()
    c = self.db.cursor()
    for row in c.execute("SELECT * FROM cache"):
      ip, mask = row
#       logging.debug('Got ip: {} with subnet: {}'.format(ip, mask))
      line = 'push "route {} {}"\n'.format(ip, mask)
      template += line
    self.db_close()
    return template





class subnets:
  
  prefixes = {
    '8': '255.0.0.0',
    '9': '255.128.0.0',
    '10': '255.192.0.0',
    '11': '255.224.0.0',
    '12': '255.240.0.0',
    '13': '255.248.0.0',
    '14': '255.252.0.0',
    '15': '255.254.0.0',
    '16': '255.255.0.0',
    '17': '255.255.128.0',
    '18': '255.255.192.0',
    '19': '255.255.224.0',
    '20': '255.255.240.0',
    '21': '255.255.248.0',
    '22': '255.255.252.0',
    '23': '255.255.254.0',
    '24': '255.255.255.0',
    '25': '255.255.255.128',
    '26': '255.255.255.192',
    '27': '255.255.255.224',
    '28': '255.255.255.240',
    '29': '255.255.255.248',
    '30': '255.255.255.252'
  }
  def get_prefix(self, item):
    try:
      ip = item.split('/')[0]
      prefix = item.split('/')[1]
      prefix = self.prefixes[prefix]
    except IndexError:
      return item, '255.255.255.255'
    return ip, prefix

  def expand(self, zones, template):
    temp = []
    for item in zones:
      ip, prefix = self.get_prefix(item)
      temp.append(
        'push "route {} {}"'.format(
          ip, prefix
        )
      )
    for i in temp:
      line = '{}\n'.format(i)
      if line not in template:
        template += line
    return template




if __name__ == '__main__':
  logcnf = {
    'level': logging.CRITICAL,
    'format': "%(asctime)s %(levelname)s %(message)s"
  }
  try:
    if os.environ['DEBUG'] == '1':
      logcnf['level'] = logging.DEBUG
  except:
    pass
  logging.basicConfig(**logcnf)


  # simply read file template
  with open('openvpn.conf', 'r') as f:
    template = f.read()

  # import zones from zones.py on top of current file
  template = subnets().expand(zones=zones, template=template)

#   # Way 1 - on-line expand
#   template = rublacklist().expand(template)

#   # Way 2 - create cache, expand from it
  rublacklist().create_cache()
  template = rublacklist().expand_from_cache(template)

  print(template)


