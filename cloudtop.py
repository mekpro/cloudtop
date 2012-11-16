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
  def __init__(self, node_name, node_uri):
    Process.__init__(self)
    self.node_name = node_name
    self.old_stats = None
    self.new_stats = None
    self.node_uri = node_uri
    self.interval = INTERVAL
    conn = pymongo.Connection("localhost", 27017, safe=True)
    self.db = conn.cloudtop
    logging.info("Connecting to %s", self.node_uri)
    self.conn = libvirt.openReadOnly(self.node_uri)

  def extract_doms_name(self, doms_stats):
    doms_name = list()
    for dom in doms_stats:
      doms_name.append(dom["domname"])
    return doms_name

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
    r['domname'] = dom.name()
    r['state'],r['mem_max'],r['mem_use'],r['ncpus'],r['cputime'] =  dom.info()
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
      dom_stats = self.get_dom_stats(dom)
      doms_stats.append(dom_stats)
    return doms_stats

  def get_node_stats(self):
    r = dict()
    r['hostname'] = self.conn.getHostname()
    r['model'],r['memory'],r['cpus'],r['mhz'],r['nodes'],r['sockets'],r['cores'],r['threads'] = self.conn.getInfo()
    r['doms_stats'] = self.get_doms()
    r['doms_name'] = self.extract_doms_name(r['doms_stats'])
    r['doms_count'] = len(r['doms_stats'])
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

    for dcur,dold in zip(stats["doms_stats"],old_stats["doms_stats"]):
      dcur['cputime'] = (dcur['cputime'] - dold['cputime']) / (1000000.0*interval)
      for disk in dcur["disks"]:
        dcur['disks_stats'][disk]['wr_bytes'] = (dcur['disks_stats'][disk]['wr_bytes'] - dold['disks_stats'][disk]['wr_bytes'])/interval
        dcur['disks_stats'][disk]['rd_bytes'] = (dcur['disks_stats'][disk]['rd_bytes'] - dold['disks_stats'][disk]['rd_bytes'])/interval
      for net in dcur["nets"]:
        dcur['nets_stats'][net]['tx_bytes'] = (dcur['nets_stats'][net]['tx_bytes'] - dold['nets_stats'][net]['tx_bytes'])/interval
        dcur['nets_stats'][net]['rx_bytes'] = (dcur['nets_stats'][net]['rx_bytes'] - dold['nets_stats'][net]['rx_bytes'])/interval
    return stats

  def mongostore(self, stats):
    doms_stats = stats.pop('doms_stats') 
    collect_time = stats["collect_time"]
    hostname = stats["hostname"]
    self.db.host.insert(stats)
    for dom in doms_stats:
      dom["collect_time"] = collect_time
      dom["hostname"] = hostname
      self.db.dom.insert(dom)

  def run(self):
    while True:
      self.new_stats = self.get_node_stats()
      if self.old_stats is None:
        logging.info("starting collection from %s", self.node_uri)
      else:
        stats = self.diff_stats(self.new_stats, self.old_stats, self.interval)
        cputime = stats['stats']['cputime']
        stats['cpu_load'] = cputime['kernel'] + cputime['user'] + cputime['iowait']
        stats['collect_time'] = datetime.datetime.utcnow()
        self.mongostore(stats)
        logging.info('collected from ' + self.node_name)
      self.old_stats = self.new_stats
      time.sleep(self.interval)

if __name__ == '__main__':
  logger = logging.getLogger('')
  logger.setLevel(logging.INFO)
  process_table = list()
  for uri in uri_list:
    logger.info(uri)
    p = GatherProcess(uri[0], uri[1])
    p.start()
    process_entry = {'name': uri[0], 'uri': uri[1], 'process': p}
    process_table.append(process_entry)

  print "Starting value gathering:"
  while True:
    time.sleep(INTERVAL)
    for p in process_table:
      if not p['process'].is_alive():
        p['process'].terminate()
        p = GatherProcess(p['name'], p['uri'])
        p.start()
        p['process'] = p
        logging.info('process' + p['name'] + ' restarted')
      else:
        logging.info('process' + p['uri'] + ' is alive')
