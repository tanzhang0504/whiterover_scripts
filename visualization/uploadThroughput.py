import sys
import MySQLdb

import upload_illegal

dataFile = ""
tableName = ""
if len(sys.argv) == 3:
    dataFile = sys.argv[1]
    tableName = sys.argv[2]
else:
    print "This script takes datarate data file as an argument and table name as second"
    sys.exit(1)

uploader = upload_illegal.DBUploader("localhost", "root", "admin123", "whitespace", tableName)

with open(dataFile, 'r') as f:
    for line in f.readlines():
        linesplit = line.split()
        curLat = float(linesplit[0])
        curLon = float(linesplit[1])
        speed = float(linesplit[2])
        throughput = float(linesplit[3])
        if throughput < 0:
            throughput = 0.0
        lossrate = float(linesplit[4])
        if lossrate < 0:
            lossrate = 1.0
        uploader.uploadThroughputs(curLat, curLon, speed, throughput, lossrate)
