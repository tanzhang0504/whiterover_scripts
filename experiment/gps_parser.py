#!/usr/bin/python

import time
import subprocess
import fcntl
import select
import os
import re
import threading
import pdb
import logging
import sys
import time

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',)
# level: CRITICAL 50, ERROR 40, WARNING 30, INFO 20, DEBUG 10, NOTSET 0, low-level message will be ignored
# %s string  %-10s left-aligned

class GPSInfo(object): # inherit object class, which is the most base type
	def __init__(self, fields = ('time', 'lat', 'lon', 'alt', 'speed')):  # () tuple, cannot change, fileds has default value(immutable)
		self._FIELDS = fields #__init__ runs when a instance of class is established 
		self._gps_info = self._make_gps_info()
		self._lock = threading.Lock() # self._lock.acquire() & self._lock.release(), in the same thread cannot acquire() >= 2 times
	
	def _make_gps_info(self):
		assert len(self._FIELDS) > 0
		dic = {}
		for field in self._FIELDS:
			dic[field] = -1.0  # each key's init value = -1.0
		return dic 

	def get_fields(self):
		return self._FIELDS
	
	def set_gps_info(self, dic):
		self._lock.acquire()
		for key in dic:
			self._gps_info[key] = dic[key]
		self._lock.release()
	
	def get_loc(self):
		self._lock.acquire()
		tup = (self._gps_info['lat'], self._gps_info['lon'])
		self._lock.release()
		return tup
	
	def get_info(self):
		info = {}
		self._lock.acquire()
		for field in self._gps_info:
			info[field] = self._gps_info[field]
		self._lock.release()
		return info

	def gps_ready(self):
		self._lock.acquire()
		is_ready = (self._gps_info['lat'] != -1.0)
		self._lock.release()
		return is_ready

	def print_info(self, f_w = None):
		if f_w is None:
			f_w = sys.stdout
		print >>f_w, "###",
		self._lock.acquire()
		for field in self._FIELDS:
			print >>f_w, "%s: %.6f" % (field, self._gps_info[field]),
		print >>f_w, ""
		self._lock.release()

class GPSParser(object):
	"""Parse the GPS readings in non-blocking mode. Set the system time periodically
	and return the most recent latitude and longitude readings.
	"""
	def __init__(self):
		self._TIME_PATTERN = "%e %B %Y %H:%M:%S" # %e day of month (1-31), %B full month name, %Y year including the century 
		self._START_PATTERN = "\"class\":\"TPV\""
		self._is_done = False
	
	def set_is_done(self, done):
		self._is_done = done
	
	def read_gps(self, gps_info, dev, read_laptop_time=False):
		cmd = "gpspipe " + dev + " -w"
		gpspipe = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE) # create a new subprocess
		mode = fcntl.fcntl(gpspipe.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK
		fcntl.fcntl(gpspipe.stdout.fileno(), fcntl.F_SETFL, mode) # file lock
		cnt = 0
		while gpspipe.poll() == None:
			readx = select.select([gpspipe.stdout.fileno()], [], [])[0]
			if readx:
				line = gpspipe.stdout.readline()
				#logging.debug(line.rstrip())
				dic = self._parse_line(line, gps_info.get_fields())
				if dic:
					cnt += 1
					if read_laptop_time:
						dic['time'] = time.time()
					gps_info.set_gps_info(dic)

			if self._is_done:
				gpspipe.terminate()
				return

	def _parse_line(self, line, fields):
		# Debug
		#dic = {}
		#dic['time'] = 1367972796.346348
		#dic['lat'] = 43.071915780
		#dic['lon'] = -89.406292909
		#dic['alt'] = 100.4
		#dic['speed'] = 1.2
		#return dic

		m_start = re.search(self._START_PATTERN, line)
		if m_start is None:
			return None
		
		dic = {}
		for field in fields:
			if field  == 'time':
				continue
			pattern = "\"%s\":\s*([+-]?(\d+)(.\d+)?)" % field # regex?
			m = re.search(pattern, line)
			if m:
				val = float(m.group(1))
				dic[field] = val
		return dic
			
	def _set_system_time(self, raw_time):
		ltime = time.localtime(raw_time)
		time_str = time.strftime(self._TIME_PATTERN, ltime)
		cmd = "date -s \"%s\"" % time_str
		os.system(cmd)


if __name__ == '__main__':
	gps_info = GPSInfo()
	gps_parser = GPSParser(5)
	gps_parser.read_gps(gps_info)
# every module has a property: __name__ 
# if directly run this .py file, __name__ == '__main__', if import this .py file, __name__ != '__main__'
