#!/usr/bin/python

import numpy
import pdb
import os
from util import create_dir

def shuffle_packet_loss(interval, arr, filename_w = None):
  segment_starts = numpy.arange(0, arr.shape[0], interval)
  L = [[] for _ in xrange(segment_starts.size)]
  inds = numpy.arange(len(L))
  numpy.random.shuffle(inds)
  for ind, start in zip(inds, segment_starts):
    L[ind] = arr[start : start + interval]
  fmt = ['%g' for _ in xrange(arr.shape[1] - 3)]
  fmt = ['%d', '%.6f', '%.6f'] + fmt
  arr_out = numpy.vstack(L)
  # first three columns are id, lat, lon.
  if filename_w:
    numpy.savetxt(filename_w, arr_out, fmt=" ".join(fmt))
  return arr_out

def calculate_capacity(data_rates, arr):
  throughput_arr = arr[:,3:].copy() 
  for no, rate in enumerate(data_rates):
    throughput_arr[:, no] = (1 - throughput_arr[:, no]) * rate
  capacity_arr = numpy.max(throughput_arr, axis=1)
  return capacity_arr

if __name__ == '__main__':
  data_rates = numpy.array([1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])
  INTERVAL = 50
  max_num_bs = 20
  max_num_clients = 20

  dirname_w = "trace"
  filename_r = "packet_loss.dat"
  create_dir(dirname_w)
  arr = numpy.loadtxt(filename_r, dtype='f8')
  for client_id in range(1, max_num_clients + 1):
    capacity_arr_total = None
    filename_w = "%s/client_%d.dat" % (dirname_w, client_id)
    for bs_id in range(1, max_num_bs + 1):
      #filename_loss = "%s/packet_loss_%d_%d.dat" % (dirname_w, bs_id, client_id)
      filename_loss = None
      synthesized_arr = shuffle_packet_loss(INTERVAL, arr, filename_loss)
      capacity_arr = calculate_capacity(data_rates, synthesized_arr)
      if capacity_arr_total is None:
        capacity_arr_total = capacity_arr
      else:
        capacity_arr_total = numpy.vstack((capacity_arr_total, capacity_arr))
    numpy.savetxt(filename_w, numpy.atleast_2d(capacity_arr_total).T, fmt="%g")
