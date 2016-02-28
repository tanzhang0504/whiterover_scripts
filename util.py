#!/usr/bin/python

import numpy
#import scipy.stats
import pdb
import os
import subprocess
import time
import re

def bin_arr(arr, bin_limits):
	"""Apply binning based on arr.
	   return bin_list and arr_list.
	   bin_list = a list of (start, end)  
	   index_list = a list of row no
	   for the last bin, [start, end]
	   Note: 1) arr is NOT assumed to be sorted in any way.
	   	     2) For an empty bin, the list entry is empty.
			 3) The order of the indices is based on the original order.
			 4) If bin_limits = [1, 2, 3], the calculated bins are [1,2), [2,3]
	"""
	assert isinstance(arr, numpy.ndarray) and isinstance(bin_limits, numpy.ndarray)
	bin_list = [ (bin_limits[no], bin_limits[no+1]) for no in range(bin_limits.size-1) ] 
	index_list = [ [] for i in range(bin_limits.size+1) ] 
	for (bin_num, index) in zip(numpy.digitize(arr, bin_limits), range(arr.size)):  
		index_list[bin_num].append(index)
	del index_list[0]
	del index_list[-1]
	# Have to append the last elements equal to the last bin
	for index in numpy.where(arr == bin_limits[-1])[0]:
		index_list[-1].append(index)
	index_list[-1].sort()  # make the indices sorted - not the values!
	assert len(bin_list) == len(index_list)
	return bin_list, index_list

def calc_dist_tup(t1, t2):
	"""The distance between two location tuples in meters."""
	assert len(t1) == 2 and len(t2) == 2
	RADIUS = 6371.  # Radius of the earth
	dist = 1000.*RADIUS * math.arccos(math.cos(math.radians(t1[0]))*math.cos(math.radians(t2[0]))*math.cos(math.radians(t2[1]-t1[1]))+math.sin(math.radians(t1[0]))*math.sin(math.radians(t2[0])))
	return dist

def calc_dist(t1, t2):
	"""The distance between two location tuples in meters."""
	assert isinstance(t1, numpy.ndarray) and isinstance(t2, numpy.ndarray)
	assert t1.shape[1] == 2 and t2.shape[1] == 2  # Should have two columns for lat and long respectively.
	RADIUS = 6371.   # Radius of the earth
	dist = 1000.*RADIUS * numpy.arccos(numpy.cos(numpy.radians(t1[:,0]))*numpy.cos(numpy.radians(t2[:,0]))*numpy.cos(numpy.radians(t2[:,1]-t1[:,1]))+numpy.sin(numpy.radians(t1[:,0]))*numpy.sin(numpy.radians(t2[:,0])))
	return dist

def add_fields(arr, descr, arr_append=None):
	""" arr is a numpy structure array and descr is a list of tuples,
		e.g. [('score', float)]
		arr_append is the data to be appended. 
	"""
	if arr.dtype.fields is None:
		raise ValueError, "arr must be a structured numpy array"
	arr_new = numpy.zeros(arr.shape, dtype=arr.dtype.descr + descr)
	for name in arr.dtype.names:
		arr_new[name] = arr[name]
	if arr_append is not None:
		assert arr_append.ndim == 2 and arr_append.shape[1] == len(descr)
		for no, pair in enumerate(descr):
			arr_new[pair[0]] = arr_append[:, no]
	return arr_new

def calc_cdf(arr, bins, bin_range=None, filename=None):
	assert arr.size > 0
	[hist_arr, bin_arr] = numpy.histogram(arr, bins=bins, range=bin_range)
	hist_arr = hist_arr.cumsum() 
	try:
		assert hist_arr[-1] == arr.size
	except:
		pdb.set_trace()
	hist_arr = hist_arr * 1.0/hist_arr[-1]
	if filename:
		numpy.savetxt(filename, numpy.hstack((bin_arr[:-1].reshape(-1, 1), hist_arr.reshape(-1, 1))), fmt='%g %g')
	return (hist_arr, bin_arr[:-1])

def calc_pdf(arr, bins, bin_range=None, filename=None, divide=True):
	[hist_arr, bin_arr] = numpy.histogram(arr, bins=bins, range=bin_range)
	assert hist_arr.sum() == arr.size
	if divide:
		if arr.size > 0:
			hist_arr = hist_arr * 1.0/arr.size  # else return raw numbers
	if filename:
		numpy.savetxt(filename, numpy.hstack((bin_arr[:-1].reshape(-1, 1), hist_arr.reshape(-1, 1))), fmt='%g %g')
	return (hist_arr, bin_arr[:-1])

def prune_arr_quartile(arr, low_percent, high_percent):
	""" Only prune out (low_percent+high_percent)% points.
		(low_percent, high_percent)"""
	assert isinstance(arr, numpy.ndarray) and len(arr.shape) == 1  # Make sure 1d array
	if low_percent == 0 and high_percent == 100:
		return arr
	arr_sort = numpy.sort(arr)
	low_start = numpy.ceil(arr_sort.size * low_percent / 100.)
	high_start = numpy.ceil(arr_sort.size * (100-high_percent) / 100.)
	return arr_sort[low_start:-1*high_start]

def enum(**enums):
	return type('Enum', (), enums)

def create_dir(dirname):
	cmd = "mkdir -p %s" % dirname
	subprocess.call(cmd, shell=True)

def find_file_nums(dirname, keyword, reverse = True):
	search_key = keyword + '_' 
	dirs = [name for name in os.listdir(dirname) if search_key in name]
	numbers = [float(dirname_power.split('_')[-1].split('.')[0]) for dirname_power in dirs]
	return sorted(numbers, reverse = reverse)

def find_files(dirname, keyword):
	files = [name for name in os.listdir(dirname) if keyword in name]
	return files

def time_to_str(time_val = None):
	fmt = "%Y-%m-%d %H:%M:%S"
	local_time = time.localtime(time_val)
	return time.strftime(fmt, local_time)

def run_cmd(cmd, sleep_time = 0):
	print cmd
	subprocess.call(cmd, shell=True)
	time.sleep(sleep_time)

def find_dates(dirname, keyword = None):
	dates = []
	pattern = "((\d+)_(\d+)_(\d+))"
	for filename in os.listdir(dirname):
		if not keyword or keyword in filename:
			m = re.search(pattern, filename)
			assert m
			dates.append(m.group(1))
	return dates
