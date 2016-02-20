#!/usr/bin/python

import sys
import os
import fcntl
import select
import math
import time
import subprocess
import threading
import re

import gps_parser

NUMBER_OF_DATARATES = 12
IPERF_PATTERN = "(\d+(.\d+)?)\s+(\w?)bits/sec.*\((\d+)\%"

def getGpsData(gpsData):
    dic = gpsData.get_info()

    lat = dic['lat']
    lon = dic['lon']
    speed = dic['speed']
    time = dic['time']
    return lat, lon, speed, time

def parse_throughput_loss_per_line(line):
    """ Return the throughput of each line of the iperf reading in 
    Mbps."""

    throughput = -1.0
    lossRate = -1.0
    m = re.search(IPERF_PATTERN, line)
    if m: 
        throughput = float(m.group(1))
        if m.group(3) == 'K':
            throughput = throughput/1000.
        elif m.group(3) == 'M':
            throughput = throughput
        else:  # in bytes
            throughput = throughput/1.e6

        #m2 = re.search(LOSS_PATTERN, line)
        #if m2:
        lossRate = float(m.group(4))
        lossRate = lossRate/100.


    return throughput, lossRate




outputFile = None
device = None

if len(sys.argv) == 3:
    outputFile = sys.argv[2]
    device = sys.argv[1]
elif len(sys.argv) == 2:
    device = sys.argv[1]
else:
    print "This script takes a device and an optional file as arguments"
    sys.exit(1)

gps_info = gps_parser.GPSInfo()
gps_parse = gps_parser.GPSParser()
thread = threading.Thread(target=gps_parser.GPSParser.read_gps, args=(gps_parse,gps_info, device))
thread.start()

time.sleep(2)

outf = open(outputFile, 'w') if outputFile else sys.stdout
cmd = "python server_udp.py"
baseratePipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
mode = fcntl.fcntl(baseratePipe.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK
fcntl.fcntl(baseratePipe.stdout.fileno(), fcntl.F_SETFL, mode) # file lock
while baseratePipe.poll() == None:
    readx = select.select([baseratePipe.stdout.fileno()], [], [])[0]
    if readx:
        while True:
            try:
                line = baseratePipe.stdout.readline()
            except IOError:
                continue
            break
        throughput, lossRate = parse_throughput_loss_per_line(line)
        lat, lon, speed, time = getGpsData(gps_info)
        outf.write(("%.6f" % lat) + " " + \
                ("%.6f" % lon) + " " + ("%.3f" % speed) + " " + str(throughput) + " " + str(lossRate) + "\n")

if outputFile != None:
    close(outf)
