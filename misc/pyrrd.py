import rrdtool, tempfile

datasources = ['DS:speed1:COUNTER:600:U:U',
               'DS:speed2:COUNTER:600:U:U',
               'DS:speed3:COUNTER:600:U:U']

rrdtool.create('speed.rrd', '--start', '920804400', datasources,
               'RRA:AVERAGE:0.5:1:24', 'RRA:AVERAGE:0.5:6:10')


info = rrdtool.info('speed.rrd')
for i in info:
  print i + " : " + str(info[i])
