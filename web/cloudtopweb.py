from bottle import route, run, template, static_file
import pymongo
import datetime

ROOT_DIR = '/root/cloudtop/web/static'
IP_BIND = '158.108.38.93'
PORT = 8080

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=ROOT_DIR)

@route('/')
def index():
  dt = datetime.datetime.now().isoformat()
  return template('index', dt=dt)

if __name__ == '__main__':
  run(host=IP_BIND, port=PORT)
