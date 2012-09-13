import os
import re

def grep(lines, pattern):
  result = []
  for l in lines:
    if re.search(pattern,l) is not None:
      result.append(l)
  return result

def parse_loadavg(loadavg_str):
  r = dict()
  arr = re.split('\D+', loadavg_str)
  r["load1m"] = arr[0] + "." + arr[1]
  r["load5m"] = arr[2] + "." + arr[3]
  r["load15m"] = arr[4] + "." + arr[5]
  return r

def parse_meminfo(meminfo_str):
  r = dict()
  lines = meminfo_str.split('\n')
  for line in lines:
    arr = line.split(":")
    key = arr[0].lower()
    value = re.split("\D+", arr[1])[1]
    r[key] = value
  return r

def parse_diskstats_targets(diskstats_str):
  r = list()
  lines = diskstats_str.split('\n')
  for line in lines:
    arr = line.split()
    target = arr[2]
    r.append(target)
  return r

def parse_diskstats(diskstats_str):
  r = list()
  lines = diskstats_str.split('\n')
  for line in lines:
    d = dict()
    # iostat
    # offset: start at 3 (+2)
    # Field 3: # of sector read
    # Field 7: # of sector written
    # Field 9: # of I/O currently in progress
    arr = line.split()
    d["target"] = arr[2]
    d["read"] = arr[5]
    d["write"] = arr[9]
    d["queue"] = arr[11]
    r.append(d)
  return r

def parse_netdev_targets(netdev_str):
  r = list()
  lines = netdev_str.split('\n')
  for line in lines:
    d = dict()
    # netdev
    arr = line.split(":")
    target = arr[0]
    r.append(target)
  return r

def parse_netdev(netdev_str):
  r = list()
  lines = netdev_str.split('\n')
  for line in lines:
    d = dict()
    arr = line.split()
    # netdev
    #
    d["target"] = arr[0].split(":")[0]
    d["recv_bytes"] = arr[1]
    d["send_bytes"] = arr[9]
    r.append(d)
  return r

# Tester
if __name__ == '__main__':
  #input cat /proc/loadavg
  proc_loadavg = '''4.37 4.21 3.48 2/355 4588'''
  loadavg = parse_loadavg(proc_loadavg)
  print loadavg

  #input cat /proc/meminfo | grep "MemTotal\|MemFree\|Buffers\|\nCached"
  proc_meminfo = '''MemTotal:        5831276 kB
MemFree:          831268 kB
Buffers:          162824 kB
Cached:          3190596 kB'''
  meminfo = parse_meminfo(proc_meminfo)
  print meminfo

#input: cat /proc/diskstats | grep "sd. \|hd. \|md. "
  proc_diskstats = '''8       0 sda 61217 14642 2915169 972724 5775756 247364 40588608 33445688 0 15711196 34416776
8      16 sdb 758 1736 6489 952 21 4 176 448 0 908 1400
9       0 md0 474 0 3786 0 21 0 144 0 0 0 0'''
  disktargets = parse_diskstats_targets(proc_diskstats)
  diskstats = parse_diskstats(proc_diskstats)
  print disktargets
  print diskstats

#input: cat /proc/net/dev | grep "eth" 
  proc_netdev = '''eth0: 590835251 1089698    0    0    0     0          0         0 41963232  355199    0    0    0     0       0          0'''
  nettargets = parse_netdev_targets(proc_netdev)
  netdev = parse_netdev(proc_netdev)
  print nettargets
  print netdev
