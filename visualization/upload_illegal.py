#!/usr/bin/python

import sys
import numpy
import MySQLdb
import pdb
import time

class DBUploader(object):
	def __init__(self, hostname, user, passwd, db_name, table):
		self._hostname = hostname
		self._user = user
		self._passwd = passwd
		self._db_name = db_name
		self._tbl_name = table
		self._data = None
		self._db = self.connect_db()
	
	def connect_db(self):
		try:
			db = MySQLdb.connect(self._hostname, self._user, self._passwd, self._db_name)
		except Exception as e:
			print e
			print "could not connect to database\\n"
			sys.exit(0)
		
		return db

	def execute(self, query):
		#print query
		c = self._db.cursor()
		c.execute(query)
		self._db.commit()

	def clear_tbl(self):
		query = "DELETE FROM %s" % (self._tbl_name)
		self.execute(query)
		
	def uploadDatarates(self, lat, lon, speed, sdr):
		query = "INSERT INTO %s (lat, lon, speed, rate10, rate20, rate55, \
				 rate60, rate90, rate110, rate120, rate180, rate240, rate360, \
				 rate480, rate540)\
				 values (%.9f, %.9f, %.9f, %.3f, %.3f, %.3f, %.3f, %.3f, \
						 %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f)" \
				 % (self._tbl_name, lat, lon, speed, sdr[0], sdr[1], sdr[2],\
				 sdr[3], sdr[4], sdr[5], sdr[6], sdr[7], sdr[8], sdr[9], \
				 sdr[10], sdr[11])
		self.execute(query)

	def uploadThroughputs(self, lat, lon, speed, throughput, lossrate):
		query = "INSERT INTO %s (lat, lon, speed, throughput, lossrate)\
					 values (%.9f, %.9f, %.9f, %.3f, %.3f)" \
					 % (self._tbl_name, lat, lon, speed, throughput, lossrate)
		self.execute(query)

if __name__ == '__main__':
	pass
