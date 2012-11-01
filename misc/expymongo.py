import pymongo

conn = pymongo.Connection("localhost", 27017, safe=True)
db = conn.cloudtop

hosts = db.host.find()

for host in hosts:
  print host

