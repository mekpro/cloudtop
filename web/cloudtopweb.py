from bottle import route, run, template, static_file
import pymongo
import datetime

import methods
import bottle_jsonrpc

ROOT_DIR = '/root/cloudtop/web/static'
IP_BIND = '158.108.38.93'
PORT = 8088

bottle_jsonrpc.register('/rpc', methods.Methods())

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=ROOT_DIR)

@route('/rpctest')
def rpctest():
  delta = datetime.timedelta(hours=1)
  end = datetime.datetime.utcnow()
  start = end - delta
  hostname = 'vm1.cloud.cpe.ku.ac.th'
  return template('templates/rpctest', start=start, end=end, hostname=hostname)

@route('/')
def index():
  dt = datetime.datetime.now().isoformat()
  return template('templates/index', dt=dt)


if __name__ == '__main__':
  run(host=IP_BIND, port=PORT)
