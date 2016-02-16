#!/usr/bin/python

import numpy
import pdb
import os

def shuffle_packet_loss(interval, filename_r, filename_w):
  arr = numpy.loadtxt(filename_r, dtype='f8')
  segment_starts = numpy.arange(0, arr.shape[0], interval)
  L = [[] for _ in xrange(segment_starts.size)]
  inds = numpy.arange(len(L))
  numpy.random.shuffle(inds)
  for ind, start in zip(inds, segment_starts):
    L[ind] = arr[start : start + interval]
  fmt = ['%g' for _ in xrange(arr.shape[1] - 3)]
  fmt = ['%d', '%.6f', '%.6f'] + fmt
  numpy.savetxt(filename_w, numpy.vstack(L), fmt=" ".join(fmt))

if __name__ == '__main__':
  dirname = "/home/wdr1/white_rover/data/packet_loss_trace"
  filename_r = "packet_loss.dat"
  filename_w = "synthesis.dat"
  INTERVAL = 50
  shuffle_packet_loss(INTERVAL, os.path.join(dirname, filename_r), os.path.join(dirname, filename_w))
