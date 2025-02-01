# WarMapPy
- Heatmap/Convex Map Generation for Wardriving with Kismet or Airodump and the option to filter to only show the desired SSID's and/or BSSID's. 
- Utilized the .kismet.csv file created from a wardrive with Airodump or the .wiglecsv file generated with a wardrive using Kismet.
- I have tested out as much as I could, with what data I had, but if you find issues, please open an issue on here.

### Updates v0.7
- Changed the input option to '--input' and '-i'. Also you can use the option multiple times to combine data. (I like to run Airodump and Kismet at the same time, so combining creates a better set of data.)  
- Modified the '--filter' ('-f') to also filter out based on BSSID. This input now takes a single option in the command or a file with multiple BSSID's and/or SSID's  

# Usage
```
      _      __         __  ___          ___
     | | /| / /__ _____/  |/  /__ ____  / _ \__ __
     | |/ |/ / _ `/ __/ /|_/ / _ `/ _ \/ ___/ // /
     |__/|__/\_,_/_/ /_/  /_/\_,_/ .__/_/   \_, /
       v0.7     #Waffl3ss       /_/        /___/

usage: WarMapPy.py [-h] --input INPUT [INPUT ...] --output {heatmap,convex} --prefix PREFIX [--maptype {normal,terrain}] [--filter FILTER]

Generate maps from Wigle or Airodump CSV data.

options:
  -h, --help            show this help message and exit
  --input INPUT [INPUT ...], -i INPUT [INPUT ...]
                        Input CSV file(s) (Wigle or Airodump).
  --output {heatmap,convex}, -o {heatmap,convex}
                        Type of map to generate.
  --prefix PREFIX, -p PREFIX
                        Prefix for the output file name.
  --maptype {normal,terrain}, -m {normal,terrain}
                        Map type (normal or terrain).
  --filter FILTER, -f FILTER
                        SSID or BSSID to filter, or a file containing a list of SSIDs or BSSIDs.
```
### Examples

```
./WarMapPy.py -i Test.kismet.csv -o convex -p Test -m normal
./WarMapPy.py -i Test.wiglecsv -o heatmap -p Test -m terrain --filter SSIDs.txt
./WarMapPy.py -i Test.kismet.csv Test.wiglecsv -o convex -p Test --filter "CIA Surveillance Van 5"
```
