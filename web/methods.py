import pymongo
import logging
import datetime
import iso8601

class Methods:
  def __db__(self):
    conn = pymongo.Connection('localhost',27017)
    return conn.cloudtop

  def get_host_stats(self, start_str, end_str, hostname):
    db = self.__db__()
    start = iso8601.parse_date(start_str)
    end = iso8601.parse_date(end_str)
    r = dict()
    last_host = db.host.find_one({
      'hostname' : hostname,
      'collect_time' : {"$gt": start, "$lte": end},
    })
    r['info'] = dict()
    r['info']['hostname'] = last_host['hostname']
    r['info']['last_update'] = str(last_host['collect_time'])
    r['info']['cpus'] = last_host['cpus']
    r['info']['doms_count'] = last_host['doms_count']

    host_stats = db.host.find({
      'hostname' : hostname,
      'collect_time' : {"$gt": start, "$lte": end},
    }).sort('collect_time')
    r['graph'] = dict()
    r['graph']['cputime'] = dict()
    r['graph']['cputime']['params'] = dict()
    r['graph']['cputime']['data'] = list()
    r['graph']['cputime']['data'].append(list())
    r['graph']['cputime']['data'].append(list())
    r['graph']['cputime']['data'].append(list())
    r['graph']['cputime']['data'].append(list())
    r['graph']['mem'] = dict()
    r['graph']['mem']['params'] = dict()
    r['graph']['mem']['data'] = list()
    r['graph']['mem']['data'].append(list())
    r['graph']['mem']['data'].append(list())
    r['graph']['mem']['data'].append(list())
    r['graph']['mem']['data'].append(list())
    #r['graph']['disk']
    i = 0
    for stat in host_stats:
      r['graph']['cputime']['data'][0].append((i,stat['stats']['cputime']['kernel']))
      r['graph']['cputime']['data'][1].append((i,stat['stats']['cputime']['idle']))
      r['graph']['cputime']['data'][2].append((i,stat['stats']['cputime']['user']))
      r['graph']['cputime']['data'][3].append((i,stat['stats']['cputime']['iowait']))
      r['graph']['mem']['data'][0].append((i,stat['stats']['mem']['cached']))
      r['graph']['mem']['data'][1].append((i,stat['stats']['mem']['total']))
      r['graph']['mem']['data'][2].append((i,stat['stats']['mem']['buffers']))
      r['graph']['mem']['data'][3].append((i,stat['stats']['mem']['free']))
      i = i+1
    return r

  def get_doms_stats_from_host(self, start_str, end_str, hostname):
    db = self.__db__()
    start = iso8601.parse_date(start_str)
    end = iso8601.parse_date(end_str)
    r = list()
    doms_name = db.dom.find({
      'hostname' : hostname,
      'collect_time' : {"$gt": start, "$lte": end},
    }).distinct('domname')
    for domname in doms_name:
      dom = dict()
      stats = db.dom.find({
        'hostname' : hostname,
        'domname' : domname,
        'collect_time' : {"$gt": start, "$lte": end},
      })
      dom['info'] = dict()
      dom['info']['domname'] = domname
      dom['info']['last_update'] = end
      dom['graph'] = dict()
      dom['graph']['cpu'] = dict()
      dom['graph']['cpu']['params'] = dict()
      dom['graph']['cpu']['data'] = list()
      dom['graph']['cpu']['data'].append(list())
      dom['graph']['mem'] = dict()
      dom['graph']['mem']['params'] = dict()
      dom['graph']['mem']['data'] = list()
      dom['graph']['mem']['data'].append(list())
      # dom['graph']['net']
      # dom['graph']['disk']
      i = 0
      for stat in stats:
        dom['graph']['cpu']['data'][0].append((i,stat['cputime']))
        dom['graph']['mem']['data'][0].append((i,stat['mem_use']))
        i = i+1
      r.append(dom)
    return r

  def get_overview(self, start_str, end_str):
    db = self.__db__()
    hosts = db.host.distinct('hostname')
    host_stats = list()
    for hostname in hosts:
      host_stats.append(self.get_host_stats(start_str, end_str, hostname))
    return host_stats

if __name__ == '__main__':
  method = Methods()
  delta = datetime.timedelta(minutes=5)
  end = datetime.datetime.utcnow()
  start = end - delta

  hostlist = ['vm1.cloud.cpe.ku.ac.th',
#    'vm2.cloud.cpe.ku.ac.th',
#    'vm3.cloud.cpe.ku.ac.th'
  ]

  result = method.get_overview(str(start), str(end))
#  for i in range(0,1):
#    for hostname in hostlist:
#      result = method.get_host_stats(str(start), str(end), hostname)
#      result = method.get_doms_stats_from_host(str(start), str(end) ,hostname)

  print result

