from multiprocessing.queues import Queue 
from multiprocessing import Process
from multiprocessing import Pool

import libvirt
import time
import sys

uri_list = [
  "qemu+ssh://root@158.108.34.67/system",
  "",]
INTERVAL = 1.0
VIRT_CONNECT_TIMEOUT = 5

class GatherProcess(Process):
  def __init__(self, uri, queue):
    Process.__init__(self)
    self.queue = queue
    self.conn = libvirt.openReadOnly(uri)

  def queryDomInfo(self, dom):
    dominfo = dict()
    dominfo['state'],dominfo['maxmem'],dominfo['memory'],dominfo['ncpus'],dominfo['cputime'] =  dom.info()
    net_target = "venet0"
    disk_target = "vda"
#    interfaceStats = dom.interfaceStats(net_target)
#    dominfo['net_rx_bytes'] = interfaceStats[0]
#    dominfo['net_tx_bytes'] = interfaceStats[4]
#    diskStats =  dom.blockStats("disk_target")
#    dominfo['disk_rd_bytes'] = diskStats[1]
#    dominfo['disk_wr_bytes'] = diskStats[3]
    return dominfo

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

  def get_host_info(self):
    r = dict()
    r['hostname'] = self.conn.getHostname()
    r['model'],r['memory'],r['cpus'],r['mhz'],r['nodes'],r['sockets'],r['cores'],r['threads'] = self.conn.getInfo()
    r['doms'] = self.doms_info()
    return r

  def run(self):
    while True:
      hostinfo = self.get_host_info()
      self.queue.put(hostinfo)
      time.sleep(INTERVAL)

if __name__ == '__main__':
  queue = Queue()
  process_list = list()
  for uri in uri_list:
    p = GatherProcess(uri, queue)
    p.start()
    process_list.append(p)

  print "Starting value gathering:"
  #Listen Value
  while True:
    print queue.get()


