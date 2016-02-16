#!/usr/bin/python2.7
import sys, os
import MySQLdb

def get_loss_rate(rate, data):
  lossrate = -1
  if rate == 1:
    lossrate = data[5]
  elif rate == 2:
    lossrate = data[6]
  elif rate == 5.5:
    lossrate = data[7]
  elif rate == 6:
    lossrate = data[8]
  elif rate == 9:
    lossrate = data[9]
  elif rate == 11:
    lossrate = data[10]
  elif rate == 12:
    lossrate = data[11]
  elif rate == 18:
    lossrate = data[12]
  elif rate == 24:
    lossrate = data[13]
  elif rate == 36:
    lossrate = data[14]
  elif rate == 48:
    lossrate = data[15]
  elif rate == 54:
    lossrate = data[16]

  return lossrate

def download_data(tbl_name, filename):
  query = "select * from %s order by id" % tbl_name
  db = MySQLdb.connect("localhost","root","admin123","whitespace")
  c = db.cursor()
  c.execute(query)
  rows = c.fetchall()

  with open(filename, 'w') as f: 
    print >>f, "###id lat lon 1 2 5.5 6 9 11 12 18 24 36 48 54"
    for row in rows:
      for no, field in enumerate(row):
        if no != 1 and no != 4:
          if no == 2 or no == 3:
            print >>f, "%.6f" % field,
          else:
            print >>f, "%g" % field,
      print >>f

if __name__ == '__main__':
  tbl_name = "datarates_wspace_4w"
  dirname = "/home/wdr1/white_rover/data/packet_loss_trace"
  filename = "%s/packet_loss.dat" % dirname 
  download_data(tbl_name, filename)
