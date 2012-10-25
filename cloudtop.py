from multiprocessing.queues import Queue 
from multiprocessing import Process
from multiprocessing import Pool

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
INTERVAL = 1.0
VIRT_CONNECT_TIMEOUT = 5

class GatherProcess(Process):
  def __init__(self, node_name, node_uri, queue):
    Process.__init__(self)
    self.node_name = node_name
    self.queue = queue
    self.old_stats = None
    self.new_stats = None
    self.node_uri = node_uri
    logging.info("connecting to %s", self.node_uri)
    self.conn = libvirt.openReadOnly(node_uri)


  def queryDomInfo(self, dom):
    r = dict()
    r['state'],r['maxmem'],r['memory'],r['ncpus'],r['cputime'] =  dom.info()
    r['name'] = dom.name()
    r['uuid'] = dom.UUID()
    net_target = "venet0"
    disk_target = "vda"
#    interfaceStats = dom.interfaceStats(net_target)
#    r['net_rx_bytes'] = interfaceStats[0]
#    r['net_tx_bytes'] = interfaceStats[4]
#    diskStats =  dom.blockStats("disk_target")
#    r['disk_rd_bytes'] = diskStats[1]
#    r['disk_wr_bytes'] = diskStats[3]
    return r

  def doms_info(self):
    doms = list()
    domsinfo = list()
    domids = self.conn.listDomainsID()
    for domid in domids:
      dom = self.conn.lookupByID(domid)
      doms.append(dom)
    for dom in doms:
      domsinfo.append(self.queryDomInfo(dom))
    return domsinfo

  def get_node_stats(self):
    r = dict()
    r['hostname'] = self.conn.getHostname()
    r['model'],r['memory'],r['cpus'],r['mhz'],r['nodes'],r['sockets'],r['cores'],r['threads'] = self.conn.getInfo()
    r['doms'] = self.doms_info()
    return r

  def compute_stats(self, new_stats, old_stats):
    stats = new_stats
    # TODO: compute meaningful stat from different timeframe
    # eg. rate of cpu usage from differential over the time
    return stats

  def rrdstore(self, stats):
    # TODO: store value in rrd file
    logging.info("rrdstore :"+ str(stats))
    return stats

  def run(self):
    while True:
      self.new_stats = self.get_node_stats()
      if self.old_stats is None:
        logging.info("starting collection from %s", self.node_uri)
      else:
        stats = self.compute_stats(self.new_stats, self.old_stats)
        self.rrdstore(stats)
        self.queue.put(stats)
      self.old_stats = self.new_stats
      time.sleep(INTERVAL)

if __name__ == '__main__':
  logger = logging.getLogger('')
  logger.setLevel(logging.INFO)
  queue = Queue()
  process_list = list()
  for uri in uri_list:
    logger.info(uri)
    p = GatherProcess(uri[0], uri[1], queue)
    p.start()
    process_list.append(p)

  print "Starting value gathering:"
  #Listen Value
  while True:
    print queue.get()

