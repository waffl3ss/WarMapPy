#!/usr/bin/python3

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import argparse, pyfiglet, sys, json, numpy, sqlite3, geopandas
from argparse import RawTextHelpFormatter
from scipy.spatial import ConvexHull, convex_hull_plot_2d
from shapely.geometry import Polygon
from pathlib import Path

prebanner = pyfiglet.figlet_format("WarMapPy")
banner = "\n" + prebanner + "\tv0.3\tWaffl3ss\n\tOriginal from @MattBurch\n"
print(banner)

parser = argparse.ArgumentParser(description='Heatmap generator for wireless signal bleed', formatter_class=RawTextHelpFormatter)
parser.add_argument('-f', dest='gpsFile', default='', required=True, help='GPS Input File')
parser.add_argument('-b', dest='bssid', default='', required=False, help='BSSID to extract (line seperated file, comma seperated list, or single bssid')
parser.add_argument('-o', dest='outFile', default='', required=True, help='HTML Output File')
parser.add_argument('-a', dest='aerodump', default=False, required=False, help='Switch to specify Aerodump GPS file is being used', action='store_true')
parser.add_argument('-k', dest='kismet', default=False, required=False, help='Switch to specify Kismet Database file is being used', action='store_true')
parser.add_argument('-api', dest='googleAPI', default='', required=False, help='Google Maps API Key')
args = parser.parse_args()

gpsFile = str(args.gpsFile) #String
bssid = str(args.bssid) #String
outFile = str(args.outFile) #String
aerodump = args.aerodump #Bool
kismet = args.kismet #Bool
googleAPI = str(args.googleAPI) #String

if not aerodump and not kismet:
	print('[!] ERROR! Requires either a KismetDB (-k) or aerodump (-a) option\n')
	sys.exit()
elif aerodump and kismet:
	print('[!] ERROR! Only supply one option, either a KismetDB (-k) or an aerodump (-a) option\n')
	sys.exit()
if kismet and not bssid:
  print('[!] ERROR! Kismet option requires a BSSID, a list of BSSID\'s, or a line seperated file containing BSSID\'s')

def parseAeroGPS(gpsFile):
  inputfile = open(gpsFile, "r")
  Points = []
  for line in inputfile:
    if line.startswith('{"class":"TPV"') and '"mode":3' in line:
      coordinates = json.loads(line)
      latcoord = str(coordinates['lat'])
      lngcoord = str(coordinates['lon'])
      Points.append(latcoord + ',' + lngcoord + ',0, ')
  inputfile.close()
  return Points

coordList = []

def parseKismet(gpsFile, bssidFile):
  con = sqlite3.connect(gpsFile)
  cur = con.cursor()
  cur.execute('SELECT device FROM devices')
  FullList = cur.fetchall()

  pointList = []
  bssidList = []

  if Path(bssidFile).is_file():
    bssidFile = open(bssidFile, "r")
    for bssid in bssidFile.readlines():
      bssidList.append(str(bssid.strip().upper()))
  elif "," in bssidFile:
    for bssid in bssidFile.split(','):
      bssidList.append(str(bssid.strip().upper()))
  else:
    bssidList.append(str(bssidFile.strip().upper()))

  for line in FullList:
    deviceInfo = str(line).replace("(b\'", "").replace("\',)", "")
    try:
      deviceJson = json.loads(deviceInfo)
    except:
      pass

    try:
      macAddr = deviceJson["kismet.device.base.macaddr"]
      if str(macAddr) in bssidList:

        try:
          deviceBaseLocation = deviceJson["kismet.device.base.location"]["kismet.common.location.avg_loc"]["kismet.common.location.geopoint"]
          deviceBaseLocationLat = deviceBaseLocation[1]
          deviceBaseLocationLng = deviceBaseLocation[0]
          coordList.append("%s, %s" % (deviceBaseLocationLat, deviceBaseLocationLng))
        except:
          print("test")
          pass

        try:
          commonLocationLast = deviceJson["kismet.device.base.location"]["kismet.common.location.last"]["kismet.common.location.geopoint"]
          commonLocationLastLat = commonLocationLast[1]
          commonLocationLastLng = commonLocationLast[0]
          coordList.append("%s, %s" % (commonLocationLastLat, commonLocationLastLng))
        except:
          print("test")
          pass

        try:
          commonLocationMaxLoc = deviceJson["kismet.device.base.location"]["kismet.common.location.max_loc"]["kismet.common.location.geopoint"]
          commonLocationMaxLocLat = commonLocationMaxLoc[1]
          commonLocationMaxLocLng = commonLocationMaxLoc[0]
          coordList.append("%s, %s" % (commonLocationMaxLocLat, commonLocationMaxLocLng))
        except:
          print("test")
          pass

        try:
          commonLocationMinLoc = deviceJson["kismet.device.base.location"]["kismet.common.location.min_loc"]["kismet.common.location.geopoint"]
          commonLocationMinLocLat = commonLocationMinLoc[1]
          commonLocationMinLocLng = commonLocationMinLoc[0]
          coordList.append("%s, %s" % (commonLocationMinLocLat, commonLocationMinLocLng))
        except:
          print("test")
          pass

        try:
          deviceBaseSignal = deviceJson["kismet.device.base.signal"]["kismet.common.signal.peak_loc"]["kismet.common.location.geopoint"]
          deviceBaseSignalLat = deviceBaseSignal[1]
          deviceBaseSignalLng = deviceBaseSignal[0]
          coordList.append("%s, %s" % (deviceBaseSignalLat, deviceBaseSignalLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLocationAvgLoc = deviceJson["dot11.device"]["dot11.device.advertised_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.avg_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLocationAvgLocLat = dot11DeviceLocationAvgLoc[1]
          dot11DeviceLocationAvgLocLng = dot11DeviceLocationAvgLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLocationAvgLocLat, dot11DeviceLocationAvgLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLocationLastLoc = deviceJson["dot11.device"]["dot11.device.advertised_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.last"]["kismet.common.location.geopoint"]
          dot11DeviceLocationLastLocLat = dot11DeviceLocationLastLoc[1]
          dot11DeviceLocationLastLocLng = dot11DeviceLocationLastLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLocationLastLocLat, dot11DeviceLocationLastLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLocationMaxLoc = deviceJson["dot11.device"]["dot11.device.advertised_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.max_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLocationMaxLocLat = dot11DeviceLocationMaxLoc[1]
          dot11DeviceLocationMaxLocLng = dot11DeviceLocationMaxLoc [0]
          coordList.append("%s, %s" % (dot11DeviceLocationMaxLocLat, dot11DeviceLocationMaxLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLocationMinLoc = deviceJson["dot11.device"]["dot11.device.advertised_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.min_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLocationMinLocLat = dot11DeviceLocationMinLoc[1]
          dot11DeviceLocationMinLocLng = dot11DeviceLocationMinLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLocationMinLocLat, dot11DeviceLocationMinLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceRespondSSIDMapAvgLoc = deviceJson["dot11.device"]["dot11.device.responded_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.avg_loc"]["kismet.common.location.geopoint"]
          dot11DeviceRespondSSIDMapAvgLocLat = dot11DeviceRespondSSIDMapAvgLoc[1]
          dot11DeviceRespondSSIDMapAvgLocLng = dot11DeviceRespondSSIDMapAvgLoc[0]
          coordList.append("%s, %s" % (dot11DeviceRespondSSIDMapAvgLocLat, dot11DeviceRespondSSIDMapAvgLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceRespondSSIDMapLastLoc = deviceJson["dot11.device"]["dot11.device.responded_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.last"]["kismet.common.location.geopoint"]
          dot11DeviceRespondSSIDMapLastLocLat = dot11DeviceRespondSSIDMapLastLoc[1]
          dot11DeviceRespondSSIDMapLastLocLng = dot11DeviceRespondSSIDMapLastLoc[0]
          coordList.append("%s, %s" % (dot11DeviceRespondSSIDMapLastLocLat, dot11DeviceRespondSSIDMapLastLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceRespondSSIDMapMaxLoc = deviceJson["dot11.device"]["dot11.device.responded_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.max_loc"]["kismet.common.location.geopoint"]
          dot11DeviceRespondSSIDMapMaxLocLat = dot11DeviceRespondSSIDMapMaxLoc[1]
          dot11DeviceRespondSSIDMapMaxLocLng = dot11DeviceRespondSSIDMapMaxLoc[0]
          coordList.append("%s, %s" % (dot11DeviceRespondSSIDMapMaxLocLat, dot11DeviceRespondSSIDMapMaxLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceRespondSSIDMapMinLoc = deviceJson["dot11.device"]["dot11.device.responded_ssid_map"][0]["dot11.advertisedssid.location"]["kismet.common.location.min_loc"]["kismet.common.location.geopoint"]
          dot11DeviceRespondSSIDMapMinLocLat = dot11DeviceRespondSSIDMapMinLoc[1]
          dot11DeviceRespondSSIDMapMinLocLng = dot11DeviceRespondSSIDMapMinLoc[0]
          coordList.append("%s, %s" % (dot11DeviceRespondSSIDMapMinLocLat, dot11DeviceRespondSSIDMapMinLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLastBeaconedSSIDRecordAvgLoc = deviceJson["dot11.device"]["dot11.device.last_beaconed_ssid_record"]["dot11.advertisedssid.location"]["kismet.common.location.avg_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLastBeaconedSSIDRecordAvgLocLat = dot11DeviceLastBeaconedSSIDRecordAvgLoc[1]
          dot11DeviceLastBeaconedSSIDRecordAvgLocLng = dot11DeviceLastBeaconedSSIDRecordAvgLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLastBeaconedSSIDRecordAvgLocLat, dot11DeviceLastBeaconedSSIDRecordAvgLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLastBeaconedSSIDRecordLastLoc = deviceJson["dot11.device"]["dot11.device.last_beaconed_ssid_record"]["dot11.advertisedssid.location"]["kismet.common.location.last"]["kismet.common.location.geopoint"]
          dot11DeviceLastBeaconedSSIDRecordLastLocLat = dot11DeviceLastBeaconedSSIDRecordLastLoc[1]
          dot11DeviceLastBeaconedSSIDRecordLastLocLng = dot11DeviceLastBeaconedSSIDRecordLastLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLastBeaconedSSIDRecordLastLocLat, dot11DeviceLastBeaconedSSIDRecordLastLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLastBeaconedSSIDRecordMaxLoc = deviceJson["dot11.device"]["dot11.device.last_beaconed_ssid_record"]["dot11.advertisedssid.location"]["kismet.common.location.max_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLastBeaconedSSIDRecordMaxLocLat = dot11DeviceLastBeaconedSSIDRecordMaxLoc[1]
          dot11DeviceLastBeaconedSSIDRecordMaxLocLng = dot11DeviceLastBeaconedSSIDRecordMaxLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLastBeaconedSSIDRecordMaxLocLat, dot11DeviceLastBeaconedSSIDRecordMaxLocLng))
        except:
          print("test")
          pass

        try:
          dot11DeviceLastBeaconedSSIDRecordMinLoc = deviceJson["dot11.device"]["dot11.device.last_beaconed_ssid_record"]["dot11.advertisedssid.location"]["kismet.common.location.min_loc"]["kismet.common.location.geopoint"]
          dot11DeviceLastBeaconedSSIDRecordMinLocLat = dot11DeviceLastBeaconedSSIDRecordMinLoc[1]
          dot11DeviceLastBeaconedSSIDRecordMinLocLng = dot11DeviceLastBeaconedSSIDRecordMinLoc[0]
          coordList.append("%s, %s" % (dot11DeviceLastBeaconedSSIDRecordMinLocLat, dot11DeviceLastBeaconedSSIDRecordMinLocLng))
        except:
          print("test")
          pass

        minSignal = deviceJson["kismet.device.base.signal"]["kismet.common.signal.min_signal"]
        maxSignal = deviceJson["kismet.device.base.signal"]["kismet.common.signal.max_signal"]

        deviceCoords = deviceJson["kismet.device.base.signal"]["kismet.common.signal.peak_loc"]["kismet.common.location.geopoint"]
        pointList.append("%s, %s, %s, %s, %s" % (deviceCoords[1], deviceCoords[0], minSignal, maxSignal, macAddr))
    except:
      pass
  return pointList

originalTemplate = '''
<!DOCTYPE HTML SYSTEM>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>WarMap</title>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
    <script type="text/javascript" src="http://hpneo.github.io/gmaps/gmaps.js"></script>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://mattburch.github.io/warmap-go/src/all.css" rel="stylesheet">
    <style>
      #map {
        display: block;
        width: 100%;
        height: 700;
      }
    </style>
  </head>
  <body>
    <div class="container" style="margin-left: 30px; margin-right: 30px; width: 95%">
      <div class="row">
        <div class="col-xs-12">
				  <div class="row">
					  <p>
						  <div class="col-xs-2"></div>
						  <div class="col-xs-2" style="padding-bottom: 10px">Mapped Points: {{.PathLength}}</div>
						  <div class="col-xs-2">Strongest DB: {{.HighDB}}</div>
						  <div class="col-xs-2">Weakest DB: {{.LowDB}}</div>
					  </p>
          </div>
        </div>
      </div>
			<div class="row">
        <div class="col-xs-1">
            <div class="row">
              <div style="padding-top: 10px"></div>
              <p>
                <button title="Toggle Heatmap" onclick="toggleHeatmap()"><i class="fas fa-fire fa-2x" style="padding-top: 3px"></i></button>
                &nbsp;
                <button title="Add Ruler" onclick="addRuler()" style="width: 38px; height: 36; padding-top: 4; padding-left: 0"><i class="fas fa-ruler fa-2x"></i></i></button>
              </p>
            </div>
            <div class="row">
              <p>
                <button title="Toggle Overlay" onclick="toggleOverlay()" style="width: 38px; padding-left: 3"><i class="fab fa-battle-net fa-2x" style="padding-top: 3px"></i></button>
                &nbsp;
                <button title="Edit Overlay" onclick="overlayEditable()" style="width: 38px; height: 36; padding-top: 4; padding-left: 3"><i class="fas fa-edit fa-2x"></i></button>
              </p>
            </div>
            <div class="row">
              <p>
                <button title="Toggle Drive" onclick="toggleDrive()" style="width: 38px; height: 36; padding-top: 4; padding-left: 1"><i class="fas fa-car-crash fa-2x"></i></button>
                &nbsp;
                <button title="Edit Drive" onclick="driveEditable()" style="width: 38px; height: 36; padding-top: 4; padding-left: 3"><i class="fas fa-edit fa-2x"></i></button>
              </p>
            </div>
        </div>
				<div class="col-xs-10">
          <div style="height: 85%" id="map"></div>
        </div>
      </div>
    </div>
  </body>
  <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key={{.Apikey}}&libraries=visualization"></script>
  <script type="text/javascript" src="https://mattburch.github.io/warmap-go/src/labels.js"></script>
<script>
var heatMapData = {{.Heatmap}};
var overlayCoords = {{.ConvexHull}};
var overlayDrive = {{.Drive}};

var map = new google.maps.Map(document.getElementById('map'), {
  zoom: 16,
  center: {lat: {{.Lat}}, lng: {{.Lng}}},
  mapTypeId: 'satellite',
  mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
  controlSize: 30,
  streetViewControl: false
});

var heatmap = new google.maps.visualization.HeatmapLayer({
  data: heatMapData
});

var convexHull =  new google.maps.Polygon({
          paths: overlayCoords,
          editable: false,
          strokeColor: '#3366FF',
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor: '#3366FF',
          fillOpacity: 0.35
        });

var drive =  new google.maps.Polyline({
    path: overlayDrive,
    editable: false,
    geodesic: true,
    strokeColor: '#3366FF',
    strokeOpacity: 1.0,
  });

function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}
function toggleOverlay() {
  convexHull.setMap(convexHull.getMap() ? null : map)
}
function toggleDrive() {
  drive.setMap(drive.getMap() ? null : map)
}
function driveEditable() {
  if (drive.editable) {
    drive.setEditable(false);
  }
  else {
    drive.setEditable(true);
  }
}
function overlayEditable() {
  if (convexHull.editable) {
    convexHull.setEditable(false);
  }
  else {
    convexHull.setEditable(true);
  }
}
var lines = new Array();
function addRuler() {
  var ruler1 = new google.maps.Marker({
    position: map.getCenter(),
    map: map,
    draggable: true
  });
  var ruler2 = new google.maps.Marker({
    position: map.getCenter(),
    map: map,
    draggable: true
  });
  var ruler1label = new Label({
    map: map
  });
  var ruler2label = new Label({
    map: map
  });
  ruler1label.bindTo('position', ruler1, 'position');
  ruler2label.bindTo('position', ruler2, 'position');
  var rulerpoly = new google.maps.Polyline({
    path: [ruler1.position, ruler2.position],
    strokeColor: "#FFFF00",
    strokeOpacity: .7,
    strokeWeight: 7
  });
  rulerpoly.setMap(map);
  ruler1label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
  ruler2label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
  google.maps.event.addListener(ruler1, 'drag', function() {
    rulerpoly.setPath([ruler1.getPosition(), ruler2.getPosition()]);
    ruler1label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
    ruler2label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
  });
  google.maps.event.addListener(ruler2, 'drag', function() {
    rulerpoly.setPath([ruler1.getPosition(), ruler2.getPosition()]);
    ruler1label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
    ruler2label.set('text', distance(ruler1.getPosition().lat(), ruler1.getPosition().lng(), ruler2.getPosition().lat(), ruler2.getPosition().lng()));
  });

  google.maps.event.addListener(ruler1, 'dblclick', function() {
    ruler1.setMap(null);
    ruler2.setMap(null);
    ruler1label.setMap(null);
    ruler2label.setMap(null);
    rulerpoly.setMap(null);
  });

  google.maps.event.addListener(ruler2, 'dblclick', function() {
    ruler1.setMap(null);
    ruler2.setMap(null);
    ruler1label.setMap(null);
    ruler2label.setMap(null);
    rulerpoly.setMap(null);
  });

  // Add our new ruler to an array for later reference
  lines.push([ruler1, ruler2, ruler1label, ruler2label, rulerpoly]);
}

function distance(lat1, lon1, lat2, lon2) {
  var R = 3959; // Here's the right settings for miles and feet
  var dLat = (lat2 - lat1) * Math.PI / 180;
  var dLon = (lon2 - lon1) * Math.PI / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c;
  if (d > 1) return Math.round(d) + "mi";
  else if (d <= 1) return Math.round(d * 5280) + "ft";
  return d;
}
</script>
</html>
'''

def templateModifier(gpsPoints, googleAPI, *coordlist):
  heatmap = []
  driveData = []
  ConvexHullPoints = []
  lat_point_list = []
  lon_point_list = []

  if aerodump:
    for point in gpsPoints:
      pointLat = point.split(",")[0]
      pointLng = point.split(",")[1]
      pointDbm = point.split(",")[2]
      pointMAC = point.split(",")[3]

      heatmap.append('{location: new google.maps.LatLng(%f, %f), weight: %f}, ' % (float(pointLat), float(pointLng), float((float(pointDbm)/10.0)+9.0)))
      driveData.append('(new google.maps.LatLng(%f, %f))' % (float(pointLat), float(pointLng)))
    
      lat_point_list.append(float(pointLat))
      lon_point_list.append(float(pointLng))

      pageLat = gpsPoints[0].split(",")[0]
      pageLng = gpsPoints[0].split(",")[1]
      PathLength = len(gpsPoints)

      HighDB = str("0")
      LowDB = str("0")

  if kismet:
    for point in coordList:
      pointLat = point.split(",")[0]
      pointLng = point.split(",")[1]
      pointDbm = 0

      heatmap.append('{location: new google.maps.LatLng(%f, %f), weight: %f}, ' % (float(pointLat), float(pointLng), float((float(pointDbm)/10.0)+9.0)))
      driveData.append('(new google.maps.LatLng(%f, %f))' % (float(pointLat), float(pointLng)))

      lat_point_list.append(float(pointLat))
      lon_point_list.append(float(pointLng))

    for point in gpsPoints:
      pointLat = point.split(",")[0]
      pointLng = point.split(",")[1]
      pointMinSignal = point.split(",")[2]
      pointMaxSignal = point.split(",")[3]
      pointMAC = point.split(",")[4]
      
      lat_point_list.append(float(pointLat))
      lon_point_list.append(float(pointLng))

    pageLat = gpsPoints[0].split(",")[0]
    pageLng = gpsPoints[0].split(",")[1]
    PathLength = len(coordList)

    HighDB = str(pointMaxSignal)
    LowDB = str(pointMinSignal)

  polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
  crs = {'init': 'epsg:4326'}
  polygon = geopandas.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
  polygon_unedited = str(polygon.unary_union.convex_hull)
  RevConvexHullPoints = (polygon_unedited.split('((')[1].split('))')[0].split(","))
  for revConPoint in RevConvexHullPoints:
    if revConPoint.split(" ")[0] == '':
      convexLng = revConPoint.split(" ")[1]
      convexLat = revConPoint.split(" ")[2]
    else:
      convexLng = revConPoint.split(" ")[0]
      convexLat = revConPoint.split(" ")[1]
    ConvexHullPoints.append('(new google.maps.LatLng(%s, %s))' % (convexLat, convexLng))

  convexHullFinal = str(ConvexHullPoints).replace('\'', '')

  HeatMap = str(heatmap).replace('\'', '').replace(' , ', ' ')
  Drive = str(driveData).replace('\'', '')

  apikey = googleAPI

  newPage = originalTemplate.replace('{{.PathLength}}', str(PathLength)).replace('{{.Apikey}}',apikey).replace('{{.Heatmap}}',HeatMap).replace('{{.Drive}}',Drive).replace('{{.Lat}}',pageLat).replace('{{.Lng}}',pageLng).replace('{{.HighDB}}',HighDB).replace('{{.LowDB}}',LowDB).replace('{{.ConvexHull}}',str(convexHullFinal))
  finalFile = open(outFile, "a+")
  print(newPage, file = finalFile)
  finalFile.close()

def main():
  if not aerodump and not kismet:
    print('[!] ERROR! Requires either a KismetDB (-k) or aerodump (-a) option\n')
    sys.exit()

  elif aerodump and kismet:
    print('[!] ERROR! Only supply one option, either a KismetDB (-k) or an aerodump (-a) option\n')
    sys.exit()

  elif aerodump and not kismet:
    gpsPoints = parseAeroGPS(gpsFile)
    templateModifier(gpsPoints, googleAPI)

  elif not aerodump and kismet:
    gpsPoints = parseKismet(gpsFile, bssid)
    templateModifier(gpsPoints, googleAPI, coordList)

  else:
    print('[!] ERROR! Not sure what happened! (Will be implementing errors soon)')
    sys.exit()

if __name__ == "__main__":
  main()