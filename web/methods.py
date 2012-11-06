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
    logging.error(start)
    logging.error(type(start))
    logging.error(end)
    logging.error(type(end))
    logging.error(hostname)
    r = dict()
    last_host = db.host.find_one({
      'hostname' : hostname,
      'collect_time' : {"$gt": start, "$lte": end},
    })
    logging.error(db)
    logging.error(last_host)
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
      dom['cpu'] = dict()
      dom['cpu']['params'] = dict()
      dom['cpu']['data'] = list()
      dom['cpu']['data'].append(list())
      dom['mem'] = dict()
      dom['mem']['params'] = dict()
      dom['mem']['data'] = list()
      dom['mem']['data'].append(list())
      # dom['net']
      # dom['disk']
      i = 0
      for stat in stats:
        dom['cpu']['data'][0].append((i,stat['cputime']))
        dom['mem']['data'][0].append((i,stat['mem_use']))
        i = i+1
      r.append(dom)
    return r


if __name__ == '__main__':
  method = Methods()
  delta = datetime.timedelta(minutes=5)
  end = datetime.datetime.utcnow()
  start = end - delta

  hostlist = ['vm1.cloud.cpe.ku.ac.th',
#    'vm2.cloud.cpe.ku.ac.th',
#    'vm3.cloud.cpe.ku.ac.th'
  ]

  for i in range(0,1):
    for hostname in hostlist:
      result = method.get_host_stats(str(start), str(end), hostname)
      #result = method.get_doms_stats_from_host(str(start), str(end) ,hostname)
      print result

