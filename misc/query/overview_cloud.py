import pymongo
import datetime

conn = pymongo.Connection('localhost', 27017)
db = conn.cloudtop

hosts = db.host.distinct('hostname')

delta = datetime.timedelta(hours=1)
end = datetime.datetime.utcnow()
start = end - delta

for host in hosts:
  host_stats = db.host.find({'hostname':host,'collect_time': {"$gt" : start, "$lte" : end}})
  cpuload = list()
  domlist = list()
  for stat in host_stats:
    cpuload.append(stat["cpu_load"])
  #print cpuload
