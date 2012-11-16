import bottle
import pymongo
import datetime

import methods
import bottle_jsonrpc

ROOT_DIR = '/root/cloudtop/web/static'
IP_BIND = '158.108.38.93'
PORT = 8088

bottle_jsonrpc.register('/rpc', methods.Methods())

@bottle.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=ROOT_DIR)

@bottle.route('/rpctest')
def rpctest():
  delta = datetime.timedelta(hours=1)
  end = datetime.datetime.utcnow()
  start = end - delta
  hostname = 'vm1.cloud.cpe.ku.ac.th'
  return bottle.template('templates/rpctest', pagename="Overview", start=start, end=end, hostname=hostname)

@bottle.route('/')
def index():
  dt = datetime.datetime.now().isoformat()
  return bottle.template('templates/index', dt=dt)

@bottle.route('/host/<hostname>')
def view_host(hostname):
  dt = datetime.datetime.now().isoformat()
  delta = datetime.timedelta(hours=1)
  end = datetime.datetime.utcnow()
  start = end - delta
  return bottle.template('templates/view_host', pagename="Host", dt=dt, start=start, end=end, hostname=hostname)


if __name__ == '__main__':
  bottle.debug(True)
  bottle.run(reloader=True, host=IP_BIND, port=PORT)
