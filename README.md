# WarMapPy
Heatmap/Convex Map Generation for Wardriving with Kismet or Airodump. 

Utilized the .kismet.csv file created from a wardrive with Airodump or the .wiglecsv file generated with a wardrive using Kismet.

I have tested out as much as I could, but if you find issues, please open an issue on here.

# Usage
```
      _      __         __  ___          ___
     | | /| / /__ _____/  |/  /__ ____  / _ \__ __
     | |/ |/ / _ `/ __/ /|_/ / _ `/ _ \/ ___/ // /
     |__/|__/\_,_/_/ /_/  /_/\_,_/ .__/_/   \_, /
       v0.5     #Waffl3ss       /_/        /___/

usage: WarMapPy.py [-h] --file FILE --output {heatmap,convex} --prefix PREFIX [--maptype {normal,terrain}]
                   [--filter FILTER]

Generate maps from Wigle or Airodump CSV data.

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Input CSV file (Wigle or Airodump).
  --output {heatmap,convex}, -o {heatmap,convex}
                        Type of map to generate.
  --prefix PREFIX, -p PREFIX
                        Prefix for the output file name.
  --maptype {normal,terrain}, -m {normal,terrain}
                        Map type (normal or terrain).
  --filter FILTER       File containing a list of SSIDs to filter.
```
### Examples

```
./WarMapPy.py -f TEST.kismet.csv -o convex -p Test -m normal
./WarMapPy.py -f Test.wiglecsv -o heatmap -p Test -m terrain --filter SSIDs.txt
```
