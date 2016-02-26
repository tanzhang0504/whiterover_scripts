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
THROUGHPUT_PATTERN = "(\d+(.\d+)?)\s+(\w?)bits/sec"
LOSS_PATTERN = "\((\d+)\%"

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
    m1 = re.search(THROUGHPUT_PATTERN, line)
    if m1: 
        throughput = float(m1.group(1))
        if m1.group(3) == 'K':
            throughput = throughput/1000.
        elif m1.group(3) == 'M':
            throughput = throughput
        else:  # in bytes
            throughput = throughput/1.e6

    m2 = re.search(LOSS_PATTERN, line)
    if m2:
        lossRate = float(m2.group(1))
        lossRate = lossRate/100.
    return throughput, lossRate

if __name__ == '__main__':
    outputFile = None
    device = None
    python_script = None
    python_script = sys.arg[1]
    device = sys.argv[2]
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print "Usage: %s iperf_script gps_dev [log_file]" % sys.argv[0]
        sys.exit(0)
    else if len(sys.argv) == 4:
        outputFile = sys.argv[3]
    
    gps_info = gps_parser.GPSInfo()
    gps_parse = gps_parser.GPSParser()
    thread = threading.Thread(target=gps_parser.GPSParser.read_gps, args=(gps_parse, gps_info, device, True))
    thread.start()
    time.sleep(2)
    outf = open(outputFile, 'w') if outputFile else sys.stdout
    cmd = "python " + python_script
    baseratePipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    mode = fcntl.fcntl(baseratePipe.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(baseratePipe.stdout.fileno(), fcntl.F_SETFL, mode) # file lock
    while baseratePipe.poll() == None:
        readx = select.select([baseratePipe.stdout.fileno()], [], [])[0]
        if readx:
            while True:
                try:
                    line = baseratePipe.stdout.readline()
                    break;
                except IOError:
                    continue
            throughput, loss = parse_throughput_loss_per_line(line)
            lat, lon, speed, time = getGpsData(gps_info)
            print >>outf, "%g %.6f %.6f %.3f %.3f %g" % (time, lat, lon, speed, throughput, loss)
            outf.flush()
            
    if outputFile != None:
        outf.close()
