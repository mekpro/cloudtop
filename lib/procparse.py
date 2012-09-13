import os
import re
#input: cat /proc/loadavg
#4.37 4.21 3.48 2/355 4588
#output: dict{ "load1m": 4.37 , "load5m":4.21, "load15m": 3.48}

def parse_loadavg(loadavg_str):
  r = dict()
  splited = re.split('\D+', loadavg_str)

  return r
#  return dict{"load1m": 4.37, "load5m": 4.21, "load15m": 3.48}

#input: cat /proc/meminfo
#MemFree:        11254476 kB 
#output: dict{ "MemFree": 11254476}
def parse_meminfo(meminfo_str):
  return dict{"MemFree": 11254476}

#input: cat /proc/diskstats | grep "sd. \|hd. \|md. "
#  8       0 sda 61217 14642 2915169 972724 5775756 247364 40588608 33445688 0 15711196 34416776
#  8      16 sdb 758 1736 6489 952 21 4 176 448 0 908 1400
#  9       0 md0 474 0 3786 0 21 0 144 0 0 0 0
#output: dict{ "sda" : {} , "sdb" :{}, "md0" : {}}
def parse_diskstats(diskstats_str):
  return dict{"sda" : {"" : 1}}

#input: cat /proc/net/dev | grep "eth" 
#eth0: 590835251 1089698    0    0    0     0          0         0 41963232  355199    0    0    0     0       0          0
#output: 
def parse_netdev(netdev_str):
  return dict{"eth0" : {"" : 1}}
