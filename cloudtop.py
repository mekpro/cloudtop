from multiprocessing.queues import Queue 
from multiprocessing import Process
from multiprocessing import Pool
from lib import xmltodict

import pymongo
import copy
import json
import datetime
import logging
import libvirt
import time
import sys

uri_list = (
  ('peacewalker','qemu+ssh://root@158.108.38.93/system'),
  ('vm1.rain','qemu+ssh://root@158.108.34.5/system'),
  ('vm2.rain','qemu+ssh://root@158.108.34.6/system'),
  ('vm3.rain','qemu+ssh://root@158.108.34.7/system'),
  )

INTERVAL = 60.0
VIRT_CONNECT_TIMEOUT = 5

class GatherProcess(Process):
  def __init__(self, node_name, node_uri, queue):
    Process.__init__(self)
    self.node_name = node_name
    self.queue = queue
    self.old_stats = None
    self.new_stats = None
    self.node_uri = node_uri
    self.interval = INTERVAL
    logging.info("Connecting to %s", self.node_uri)
    self.conn = libvirt.openReadOnly(self.node_uri)
 
  def parse_dom_disks(self, xmldesc):
    result = list()
    xmld = xmltodict.parse(xmldesc)
    for i in xmld['domain']['devices']['disk']:
      result.append(i['target']['@dev'])
    return result
#   return ['vda','vdb']

  def parse_dom_nets(self, xmldesc):
    result = list()
    xmld = xmltodict.parse(xmldesc)
    interfaces = xmld['domain']['devices']['interface']
    if type(interfaces) is not list:
      result.append(interfaces['target']['@dev'])
    else:
      for i in interfaces:
        result.append(i['target']['@dev'])
    return result

  def get_dom_stats(self, dom):
    r = dict()
    r['state'],r['maxmem'],r['memory'],r['ncpus'],r['cputime'] =  dom.info()
    r['name'] = dom.name()
#    r['uuid'] = dom.UUID()
    xmldesc = dom.XMLDesc(0)
    r['nets'] = self.parse_dom_nets(xmldesc)
    r['nets_stats'] = dict()
    r['disks'] = self.parse_dom_disks(xmldesc)
    r['disks_stats'] = dict()
    for inet in r['nets']:
      inetstats = dom.interfaceStats(inet)
      r['nets_stats'][inet] = dict()
      r['nets_stats'][inet]['rx_bytes'] = inetstats[0]
      r['nets_stats'][inet]['tx_bytes'] = inetstats[4]
    for disk in r['disks']:
      diskstats = dom.blockStats(disk) 
      r['disks_stats'][disk] = dict()
      r['disks_stats'][disk]['rd_bytes'] = diskstats[1]
      r['disks_stats'][disk]['wr_bytes'] = diskstats[3]
    return r

  def get_doms(self):
    doms_stats = list()
    domids = self.conn.listDomainsID()
    for domid in domids:
      dom = self.conn.lookupByID(domid)
      doms_stats.append(self.get_dom_stats(dom))
    return doms_stats

  def get_node_stats(self):
    r = dict()
    r['hostname'] = self.conn.getHostname()
    r['model'],r['memory'],r['cpus'],r['mhz'],r['nodes'],r['sockets'],r['cores'],r['threads'] = self.conn.getInfo()
    r['doms'] = self.get_doms()
    r['doms_count'] = len(self.conn.listDomainsID())
    r['disks'] = self.conn.listStoragePools()
    r['stats'] = dict()
    r['stats']['cputime'] = self.conn.getCPUStats(-1,0)
    #{'kernel': 2531940000000L, 'idle': 1375626920000000L, 'user': 3270180000000L, 'iowait': 8155620000000L}
    r['stats']['mem'] = self.conn.getMemoryStats(-1,0)
    #{'cached': 1906532L, 'total': 16351276L, 'buffers': 454240L, 'free': 11705280L }
    r['stats']['disks'] = dict()
    for disk_name in r['disks']:
      v = dict()
      pool = self.conn.storagePoolLookupByName(disk_name)
      v['state'],v['capacity'],v['allocation'],v['available'] = pool.info()
      r['stats']['disks'][disk_name] = v
    return r

  def diff_stats(self, new_stats, old_stats, interval):
    sums = 0
    stats = copy.deepcopy(new_stats)
    for k in ['kernel','idle','user','iowait']:
      v = new_stats['stats']['cputime'][k] - old_stats['stats']['cputime'][k]
      stats['stats']['cputime'][k] = v
      sums = sums + v
    for k in ['kernel','idle','user','iowait']:
      stats['stats']['cputime'][k] = (stats['stats']['cputime'][k]*100.0)/sums
    logging.info(stats['stats']['cputime'])

    for dcur,dold in zip(stats["doms"],old_stats["doms"]):
      dcur['cputime'] = (dcur['cputime'] - dold['cputime']) / (1000000.0*interval)
      for disk in dcur["disks"]:
        logging.info(dcur)
        dcur['disks_stats'][disk]['wr_bytes'] = (dcur['disks_stats'][disk]['wr_bytes'] - dold['disks_stats'][disk]['wr_bytes'])/interval
        dcur['disks_stats'][disk]['rd_bytes'] = (dcur['disks_stats'][disk]['rd_bytes'] - dold['disks_stats'][disk]['rd_bytes'])/interval
      for net in dcur["nets"]:
        logging.info(dcur)
        dcur['nets_stats'][net]['tx_bytes'] = (dcur['nets_stats'][net]['tx_bytes'] - dold['nets_stats'][net]['tx_bytes'])/interval
        dcur['nets_stats'][net]['rx_bytes'] = (dcur['nets_stats'][net]['rx_bytes'] - dold['nets_stats'][net]['rx_bytes'])/interval
    return stats

  def run(self):
    while True:
      self.new_stats = self.get_node_stats()
      if self.old_stats is None:
        logging.info("starting collection from %s", self.node_uri)
      else:
        stats = self.diff_stats(self.new_stats, self.old_stats, self.interval)
        stats['datetime'] = datetime.datetime.now().isoformat()
        self.queue.put(stats)
      self.old_stats = self.new_stats
      time.sleep(self.interval)

if __name__ == '__main__':
  logger = logging.getLogger('')
  logger.setLevel(logging.INFO)
  queue = Queue()
  process_list = list()
  conn = pymongo.Connection("localhost", 27017, safe=True)
  db = conn.cloudtop
  for uri in uri_list:
    logger.info(uri)
    p = GatherProcess(uri[0], uri[1], queue)
    p.start()
    process_list.append(p)

  print "Starting value gathering:"
  while True:
    stats = queue.get()
    db.host.insert(stats)
