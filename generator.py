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
  
  def get_cookie(self, **kwargs):
    logging.info('Invoked get_cookie')
    return { kwargs['name']: kwargs['value'] }
  
  def is_title(self, driver, text):
    logging.info('Invoked is_title')
    try:
      assert str(text) in driver.title
      return True
    except AssertionError:
      return False
  
  def get_cf_cookies(self, url):
    logging.info('Invoked get_cf_cookies')
    logging.debug('Starting Google Chrome')
    options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=options)
    logging.debug('Opening url: {}'.format(url))
    driver.get(url)
    logging.debug('Waiting')
    sleep(20)
    while self.is_title(driver, 'Just a moment...'):
      logging.debug('Opened cloudflare check, sleep 1 sec')
      sleep(2)
#     logging.debug('Re-open url')
#     driver.get(url)
    rcookies = []
    scookies = driver.get_cookies()
    for cookie in scookies:
      rcookies.append(self.get_cookie(**cookie))
    logging.debug('Collected cookies: {}'.format(rcookies))
    return rcookies

  def get_cookies(self, url):
    logging.info('Invoked get_cookies')
    rcookies = self.get_cf_cookies(url)
    keys = []
    for rkey in rcookies:
      keys.append(
        list(
          rkey.keys()
        )[0]
      )
    logging.debug('Collected keys: {}'.format(keys))
    i = 0
    result = {}
    for key in keys:
      result[key] = rcookies[i][key]
      i += 1
    logging.debug('Collected result: {}'.format(result))
    return result

  def get_blocked_json(self):
    logging.info('Invoked get_blocked_json')
    headers = {
      'Host': 'reestr.rublacklist.net',
      'Connection': 'keep-alive',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'DNT': '1',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }
    logging.debug('Proceeding with headers: {}'.format(headers))
    url = 'https://reestr.rublacklist.net'
    cookies = dict(**self.get_cookies(url))
    url = 'https://reestr.rublacklist.net/api/v2/current/json'
    logging.debug('Proceed with cookies: {}'.format(cookies))
    logging.debug('Proceeding url: {}'.format(url))
    r = requests.get(url, headers=headers, cookies=cookies)
    logging.debug('Finished. len(data)={}'.format(len(r.text)))
    r = r.json()
    return r
  
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
      ip, prefix = subnet().get_prefix(ip)
#       logging.debug('Detected ip: {} with subnet: {}'.format(ip, prefix))
      self.db.execute(
        "INSERT INTO cache (ip, subnet) values ('{}', '{}')".format(ip, prefix)
      )
    self.db_close()

  def expand_from_cache(self, template):
    self.db_open()
    c = self.db.cursor()
    for row in c.execute("SELECT * FROM cache"):
      ip, mask = row
#       logging.debug('Got ip: {} with subnet: {}'.format(ip, mask))
      line = 'push "route {} {}"\n'.format(ip, mask)
#       if line not in template:
      template += line
    self.db_close()
    return template





class subnet:
  
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
  template = subnet().expand(zones=zones, template=template)

#   # Way 1 - on-line expand
#   template = rublacklist().expand(template)

#   # Way 2 - create cache, expand from it
  rublacklist().create_cache()
  template = rublacklist().expand_from_cache(template)

  print(template)


