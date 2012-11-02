from bottle import route, run, template
import pymongo
import datetime

IP_BIND = '158.108.38.93'
PORT = 8080

@route('/')
def index():
  dt = datetime.datetime.now().isoformat()
  return template('index', dt=dt)

if __name__ == '__main__':
  run(host=IP_BIND, port=PORT)
