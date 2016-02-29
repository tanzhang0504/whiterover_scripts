#!/usr/bin/python2.7
#Whitespace Project
import sys, os
import cgitb
import cgi
import MySQLdb
import traceback
import string
import colorsys
cgitb.enable()

def coordToStr(inp):
  inp = str(inp)
  inp = inp.replace(".","P")
  inp = inp.replace("-","M")
  return inp
def strToCoord(inp):
  inp = str(inp)
  inp = inp.replace("P",".")
  inp = inp.replace("M","-")
  return float(inp)
print "Content-Type: text/html"

def gen_color(frac):
  H = (1 - frac) * 0.4 
  S = 0.9 
  V = 0.9 
  #print H, S, V
  vals = colorsys.hsv_to_rgb(H, S, V)
  color = ''
  for val in vals:
    color += format(int(val * 255), '02x')
  color = '#' + color
  return color

def getLossRate(rate, data):
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
  

def _print(string):
  #try:
  logFile = file("test.log","a")
  logFile.write(str(string)+"\n")
  logFile.close()

_print("start")

dataPoint = {}
locations = {}
datarate = 0

form = cgi.FieldStorage()
if form.getvalue('Table') is None:
  tbl_name = "datarates_wspace_4w"
else:
  tbl_name = str(form.getvalue('Table'))

if form.getvalue('datarate') is None:
  datarate = 1
else:
  datarate = float(form.getvalue('datarate'))

tmpDr = str(int(datarate*10))

if form.getvalue('Query') is None:
  query = "'select * from " + tbl_name + "'"
else:
  query = str(form.getvalue('Query'))

query = query.replace('+',' ')
query = query[1:-1]
query += " where rate" + tmpDr + " != 1"
query += ' order by id limit 10000'

_print(query)

db = MySQLdb.connect("localhost","root","admin123","whitespace")
c = db.cursor()
c.execute(query)
rows = c.fetchall()

powers = []
for row in rows:
  s = (row[1],row[2],row[3],row[4])
  if s not in dataPoint:
    dataPoint[s] = []
    dataPoint[s].append(row)
  elif row not in dataPoint[s]:
    dataPoint[s].append(row)

for d in dataPoint:
  if (d[1],d[2],d[3]) not in locations:
    locations[(d[1],d[2],d[3])] = dataPoint[d]

circles = ""
listeners = ""
windows = ""

for l in locations:
  opacity = 1
  lossrate = getLossRate(datarate, locations[l][0])
  color=gen_color(lossrate)
  lat = str(l[0])
  lon = str(l[1])
  speed = str(l[2])
  lat = lat.replace(".","P")
  lat = lat.replace("-","M")
  lon = lon.replace(".","P") 
  lon = lon.replace("-","M")   
  markerName = "marker" + lat + lon
  circleName = "whiCirOp" + lat + lon
  radius = "10"
  content = "<a href='whitedata.py?lat="+lat+"&lon="+lon+"'>More Info</a> "
  circles += "var "+str(circleName)+" = {strokeColor: '"+"black"+"',strokeOpacity: 0.1,strokeWeight: 1,fillColor: '"+color+"',fillOpacity: "+str(opacity)+",map: map,center: new google.maps.LatLng("+str(l[0])+","+str(l[1])+"),radius: "+radius+"}; var whiCir"+circleName+" = new google.maps.Circle("+circleName+");"
  listeners += "\ngoogle.maps.event.addListener(whiCir"+circleName+", 'click', function (event) {clicker('http://128.105.22.248/whitespace/datarate_circleInfo.py?lat="+lat+"&lon="+lon+"&tblName="+tbl_name+"&datarate="+str(datarate)+"&speed="+str(speed)+"')});"

print """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
      #map-canvas { height: 100% }
      #displaybox {
        z-index: 10000;
        filter: alpha(opacity=70); /*older IE*/
        filter:progid:DXImageTransform.Microsoft.Alpha(opacity=50); /* IE */
        -moz-opacity: .70; /*older Mozilla*/
        -khtml-opacity: 0.7;   /*older Safari*/
        opacity: 0.7;   /*supported by current Mozilla, Safari, and Opera*/
        background-color:#000000;
        position:fixed; top:0px; left:0px; width:100%; height:100%; color:#FFFFFF; text-align:center; vertical-align:middle;
       }
    </style>
    <script type="text/javascript"
      src="https://maps.googleapis.com/maps/api/js?sensor=false">
    </script>
    <script type="text/javascript">
      function initialize() {
        var mapOptions = {
          center: new google.maps.LatLng(43.0761, -89.4104),
          zoom: 15,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map-canvas"),
            mapOptions);
"""
print circles
print listeners
print windows
print """
      }
      google.maps.event.addDomListener(window, 'load', initialize);
      
    </script>
    <script>
      function clicker(url){
        var thediv=document.getElementById('displaybox');
        if(thediv.style.display == "none"){
                thediv.style.display = "";
                var html = "<table width='100%' height='100%'><tr><td align='center' valign='middle' width='100%' height='100%'><iframe style='background-color:white' height='500px' width='1000px' src='";
                html += new String(url);
                html += "'></iframe><br><br><a href='#' onclick='return clicker();'>CLOSE WINDOW</a></td></tr></table>";
                thediv.innerHTML = html;
        }else{
                thediv.style.display = "none";
                thediv.innerHTML = '';
        }
        return false;
      }
    </script>
  </head>
  <body>
    <div id="displaybox" style="display: none;"></div> 
    <div id-"top-of-screen" height:40px>
      <form action="datarates_display.py">
        Query: <input type="text" name="Query" style="width:850px">
        Table: <input type="text" name="Table" style="width:50px">
        Datarate: <input type="text" name="datarate" style="width:50px">
        <input type="submit" value="Submit">
      </form>
    </div>
    <div id="map-canvas"/>
  </body>
</html>"""
