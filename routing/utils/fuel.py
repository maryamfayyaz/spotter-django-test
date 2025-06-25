import csv
from geopy.distance import geodesic

def load_fuel_data(file_path):
    stations = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                stations.append({
                    'name': row['Truckstop Name'],
                    'price': float(row['Retail Price']),
                    'lat': float(row['lat']),
                    'lon': float(row['lon']),
                })
            except (ValueError, KeyError):
                continue
    return stations

def find_cheapest_station_near(point, stations):
    for radius in [50, 75, 100]:
        nearby = [
            s for s in stations
            if geodesic(point, (s['lat'], s['lon'])).miles <= radius
        ]
        if nearby:
            return min(nearby, key=lambda s: s['price'] + 0.01 * geodesic(point, (s['lat'], s['lon'])).miles)
    return None
