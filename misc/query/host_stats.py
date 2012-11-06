import pymongo
import datetime

conn = pymongo.Connection('localhost',27017)
db = conn.cloudtop

hostname = 'vm1.cloud.cpe.ku.ac.th'
delta = datetime.timedelta(hours=1)
end = datetime.datetime.utcnow()
start = end - delta

def get_host_stats(start, end, hostname):
  r = dict()
  last_host = db.host.find_one({
    'hostname' : hostname,
    'collect_time' : {"$gt": start, "$lte": end},
  })

  r['info'] = dict()
  r['info']['hostname'] = last_host['hostname']
  r['info']['last_update'] = last_host['collect_time']
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

def get_doms_stats_from_host(start, end, hostname):
  r = list()
  doms_name = db.dom.distinct({
    'hostname' : hostname,
    'collect_time' : {"$gt": start, "$lte": end},
  })
  for dom_name in doms_name:
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
    dom['mem']['params'] = dict()
    dom['mem']['mem'].append(list())
    # dom['net']
    # dom['disk']
    i = 0
    for stat in stats:
      dom['cpu']['data'][0].append((i,stat['cputime']))
      dom['mem']['data'][0].append((i,stat['mem_use']))
      i = i+1
    r.append(dom)
  return r

result = get_host_stats(start, end ,hostname)
print result
result = get_host_stats(start, end ,hostname)
print result
