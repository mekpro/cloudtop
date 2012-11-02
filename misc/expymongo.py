import pymongo
import json
import copy

conn = pymongo.Connection("localhost", 27017, safe=True)
db = conn.cloudtop
# clear old data first
db.drop_collection('host')

fp = open('processed.json','r')
jdoc = json.load(fp)

for i in range(0,10):
  host = copy.deepcopy(jdoc) 
  host['hostname'] = 'vm'+str(i)
  db.host.insert(host)

