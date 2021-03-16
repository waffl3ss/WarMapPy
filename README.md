# WarMapPy
Python implementation of Matt Burch's (@mattburch) which uses Kismet Database or Aerodump files to overlay a WiFi coverage area on a map.

This is an early python version, please let me know if there are any issues.

WarMapPy takes a Kismet database or Aerodump gps file and creats a polygon of coordinates. The polygon is then overlayed over a generated google maps to show coverage area of a specific BSSID. In addition, a heatmap is produced which indicated the intensity of the signal strength at given points.

# Options

| Option | Information |
| ----- | ----- |
| -f | Kismet Database or Aerodump GPS file |
| -o | HTML output file |
| -b | Line seperated BSSID file, comma seperated BSSID list, or single BSSID |
| -k | Option to specify using a Kismet Database File (Requires '-b' option) |
| -a | Option to specify using an aerodump GPS file) |
| -api | Google Maps API key |

# Examples
`python3 warmap.py -f TestFile.kismet -b BSSIDs.txt -o TestOutput.html -k -api abcd1234`  
`python3 warmap.py -f TestFile.kismet -b DE:AD:BE:EF:11:22 -o TestOutput.html -k -api abcd1234`  
`python3 warmap.py -f TestFile.gps -o TestOutput.html -a -api abcd1234`

# Notes
1. When using a Kismet DB, the BSSID ('-b') option is required.
2. When collecting the Aerodump GPS file, it is impossible to differentiate the output based on BSSID. Make sure you are filtering on only the intennded ESSID/BSSID values when running Aerodump.
3. You can get your API key from [this page](https://developers.google.com/maps/documentation/javascript/get-api-key)
