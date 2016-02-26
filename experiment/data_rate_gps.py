#!/usr/bin/python

import os
import sys
import fcntl
import select
import math
import time
import subprocess
import threading

import gps_parser

NUMBER_OF_DATARATES = 12

def getGpsData(gpsData):
    dic = gpsData.get_info()

    lat = dic['lat']
    lon = dic['lon']
    speed = dic['speed']
    time = dic['time']
    return lat, lon, speed, time

outputFile = None
device = None

if __name__ == '__main__':
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
  currGroupId = 1
  outf = open(outputFile, 'w') if outputFile else sys.stdout
  workingDatarates = []
  #cmd = "python ../../src/tun_tap/wspace_client_looprate_mimo/wspace_client_looprate.py"
  #cmd = "python ../../src/tun_tap/wspace_client_looprate_11g/wspace_client_looprate.py"
  cmd = "python ../../setup/tun_tap/wspace_client_looprate.py"
  print cmd
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
		  lineSplit = line.split()
		  try:
			  packetNum = int(lineSplit[0])
		  except:
			  continue
		  try:
			  bitRate = lineSplit[1]
		  except:
			  continue
		  if packetNum - currGroupId >= NUMBER_OF_DATARATES:
			  lat, lon, speed, time= getGpsData(gps_info)
			  outf.write(("%.6f" % lat) + " " + \
				  ("%.6f" % lon) + " " + ("%.3f" % speed) + " "+ " ".join(workingDatarates) + "\n")
			  outf.flush()
			  workingDatarates = []
			  blankRecCheck = packetNum
			  blankRecCheck -= NUMBER_OF_DATARATES
			  while blankRecCheck - currGroupId >= NUMBER_OF_DATARATES:
				  outf.write("missing\n")
				  outf.flush()
				  blankRecCheck -= NUMBER_OF_DATARATES
			  currGroupId = packetNum - ((packetNum - 1) % NUMBER_OF_DATARATES)
		  workingDatarates.append(bitRate)

  if outputFile != None:
	  close(outf)
