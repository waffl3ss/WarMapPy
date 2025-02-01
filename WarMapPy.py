import argparse
import pandas as pd
import folium
from folium.plugins import HeatMap
import geopandas as gpd
from shapely.geometry import Point

def print_banner():
    banner = r"""
      _      __         __  ___          ___      
     | | /| / /__ _____/  |/  /__ ____  / _ \__ __
     | |/ |/ / _ `/ __/ /|_/ / _ `/ _ \/ ___/ // /
     |__/|__/\_,_/_/ /_/  /_/\_,_/ .__/_/   \_, / 
       v0.7     #Waffl3ss       /_/        /___/  
    """
    print(banner)

def parse_wigle(file_path):
    df = pd.read_csv(file_path, skiprows=1)
    df = df.rename(columns={
        'CurrentLatitude': 'Latitude',
        'CurrentLongitude': 'Longitude',
        'RSSI': 'Signal',
        'MAC': 'BSSID',
        'SSID': 'ESSID'
    })
    return df[['Latitude', 'Longitude', 'Signal', 'ESSID', 'BSSID']]

def parse_airodump(file_path):
    df = pd.read_csv(file_path, delimiter=';')
    df = df.rename(columns={
        'GPSBestLat': 'Latitude',
        'GPSBestLon': 'Longitude',
        'BestSignal': 'Signal',
        'BSSID': 'BSSID',
        'ESSID': 'ESSID'
    })
    df = df.dropna(subset=['Latitude', 'Longitude', 'Signal', 'ESSID', 'BSSID'])
    return df[['Latitude', 'Longitude', 'Signal', 'ESSID', 'BSSID']]

def filter_data(data, filter_value):
    filter_set = set()
    
    if filter_value:
        try:
            with open(filter_value, 'r') as f:
                filter_set.update(line.strip() for line in f)
        except FileNotFoundError:
            filter_set.add(filter_value)
    
    if filter_set:
        data = data[(data['ESSID'].isin(filter_set)) | (data['BSSID'].isin(filter_set))]
    
    return data

def create_heatmap(data, prefix, map_type="normal"):
    if data.empty:
        print("No data available to generate heatmap.")
        return

    center_lat = data['Latitude'].mean()
    center_lon = data['Longitude'].mean()
    tiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png" if map_type == "terrain" else "OpenStreetMap"
    attr = "Map data © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)"
    
    output_path = f"{prefix}_{map_type}_heatmap.html"
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles=tiles, attr=attr)
    heat_data = data[['Latitude', 'Longitude', 'Signal']].values.tolist()
    HeatMap(heat_data, radius=10).add_to(m)
    m.save(output_path)
    print(f"Heatmap saved to {output_path}")

def create_convex_map(data, prefix, map_type="normal"):
    if data.empty:
        print("No valid data available to generate convex map.")
        return

    print(f"Generating convex map with {len(data)} points.")
    gdf = gpd.GeoDataFrame(data, geometry=[Point(lon, lat) for lat, lon in zip(data['Latitude'], data['Longitude'])])
    gdf.set_crs(epsg=4326, inplace=True)

    if len(gdf) < 3:
        print("Not enough points to generate a convex hull. At least 3 points are required.")
        return

    convex_hull = gdf.geometry.union_all().convex_hull
    hull_gdf = gpd.GeoDataFrame(index=[0], geometry=[convex_hull], crs="EPSG:4326")

    center_lat = data['Latitude'].mean()
    center_lon = data['Longitude'].mean()
    tiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png" if map_type == "terrain" else "OpenStreetMap"
    attr = "Map data © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)"
    
    output_path = f"{prefix}_{map_type}_convex.html"
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles=tiles, attr=attr)
    
    for lat, lon in data[['Latitude', 'Longitude']].drop_duplicates().values:
        folium.CircleMarker(
            location=(lat, lon),
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)
    
    folium.GeoJson(
        data=hull_gdf,
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "blue",
            "weight": 2,
            "fillOpacity": 0.4,
        },
    ).add_to(m)
    
    m.save(output_path)
    print(f"Convex point map saved to {output_path}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Generate maps from Wigle or Airodump CSV data.")
    parser.add_argument("--input", "-i", required=True, nargs='+', help="Input CSV file(s) (Wigle or Airodump).")
    parser.add_argument("--output", "-o", required=True, choices=["heatmap", "convex"], help="Type of map to generate.")
    parser.add_argument("--prefix", "-p", required=True, help="Prefix for the output file name.")
    parser.add_argument("--maptype", "-m", choices=["normal", "terrain"], default="normal", help="Map type (normal or terrain).")
    parser.add_argument("--filter", "-f", help="SSID or BSSID to filter, or a file containing a list of SSIDs or BSSIDs.")
    
    args = parser.parse_args()

    data_frames = []
    for file in args.input:
        if file.endswith(".wiglecsv"):
            data_frames.append(parse_wigle(file))
        elif file.endswith(".kismet.csv"):
            data_frames.append(parse_airodump(file))
        else:
            raise ValueError("Unsupported file type. Use '.wiglecsv' for Wigle data or '.kismet.csv' for Airodump data.")
    
    data = pd.concat(data_frames, ignore_index=True)
    data = filter_data(data, args.filter)
    
    if data.empty:
        print("No data to process after filtering.")
        return

    if args.output == "heatmap":
        create_heatmap(data, args.prefix, map_type=args.maptype)
    elif args.output == "convex":
        create_convex_map(data, args.prefix, map_type=args.maptype)
    else:
        raise ValueError("Invalid output type.")

if __name__ == "__main__":
    main()
