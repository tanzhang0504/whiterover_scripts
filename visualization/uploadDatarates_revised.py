#!/usr/bin/python

import sys
import MySQLdb
import upload_illegal

if __name__ == '__main__':
	possibleDatarates = ["10", "20", "55", "60", "90", "110", "120", "180","240", "360", "480", "540"]

	dataFile = ""
	tableName = ""
	if len(sys.argv) == 3:
		dataFile = sys.argv[1]
		tableName = sys.argv[2]
	else:
		print "This script takes datarate data file as an argument and table name as second"
		sys.exit(1)

	with open(dataFile, 'r') as f:
		recDataRates = [0] * len(possibleDatarates)
		curLat = ""
		curLon = ""
		speed = ""
		totLines = 0
		missingLines = 0
		uploader = upload_illegal.DBUploader("localhost", "root", "admin123", "whitespace", tableName)

		for line in f.readlines():
			linesplit = line.split()
			if linesplit[0] == "missing":
				missingLines += 1
				continue
			if (curLat != linesplit[1] or curLon != linesplit[2] or speed != linesplit[3]):
				if totLines != 0:
					percentRec = []
					for i in range(len(recDataRates)):
						newNum = 1.0 - round(float(recDataRates[i])/float(totLines),3)
						percentRec.append(newNum)
					uploader.uploadDatarates(float(curLat), float(curLon), float(speed), percentRec)
				totLines = 0
				missingLines = 0
				recDataRates = [0] * len(possibleDatarates)
				curLat = linesplit[1]
				curLon = linesplit[2]
				speed = linesplit[3]
			else:
				totLines += missingLines
				missingLines = 0
			totLines += 1
			for x in range(4, len(linesplit)):
				recDataRates[possibleDatarates.index(linesplit[x])] += 1
	percentRec = []
	for i in range(len(recDataRates)):
		newNum = 1.0 - round(float(recDataRates[i])/float(totLines),3)
		percentRec.append(newNum)
	uploader.uploadDatarates(float(curLat), float(curLon), float(speed), percentRec)
