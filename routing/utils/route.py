import requests, polyline
from geopy.distance import geodesic
from .fuel import find_cheapest_station_near

VEHICLE_RANGE_MILES = 500
MPG = 10

def fetch_route(start, end, api_key):
    resp = requests.post(
        'https://api.openrouteservice.org/v2/directions/driving-car',
        json={'coordinates': [start[::-1], end[::-1]]},
        headers={'Authorization': api_key}
    )
    resp.raise_for_status()
    return resp.json()

def decode_route_geometry(route_json):
    route = route_json['routes'][0]
    geometry = route['geometry']
    coords = polyline.decode(route['geometry'])
    distance_meters = route['segments'][0]['distance']
    return coords, distance_meters, geometry

def plan_fuel_stops(coords, distance_meters, stations):
    total_miles = distance_meters / 1609.34
    num_stops = int(total_miles // VEHICLE_RANGE_MILES)

    step = max(1, int(len(coords) * (300 * 1609.34) / distance_meters))
    sampled_points = [coords[i] for i in range(0, len(coords), step)]

    fuel_stops, seen = [], set()
    i = 0
    while len(fuel_stops) < num_stops and i < len(sampled_points):
        candidates = []
        for j in range(i, min(i + 3, len(sampled_points))):
            pt = sampled_points[j]
            s = find_cheapest_station_near(pt, stations)
            if s:
                key = (round(s['lat'], 4), round(s['lon'], 4))
                if key not in seen:
                    candidates.append(s)
        if candidates:
            best = min(candidates, key=lambda s: s['price'])
            fuel_stops.append(best)
            seen.add((round(best['lat'], 4), round(best['lon'], 4)))
        i += 3

    gallons = total_miles / MPG
    cost = sum((gallons / len(fuel_stops)) * s['price'] for s in fuel_stops) if fuel_stops else 0

    warning = None
    if len(fuel_stops) < num_stops:
        warning = (
            f"Only {len(fuel_stops)} fuel stop(s) found, "
            f"but {num_stops} needed to avoid running out of fuel. "
            f"Some segments may be longer than {VEHICLE_RANGE_MILES} miles without a nearby station."
        )

    return {
        'distance_miles': round(total_miles, 2),
        'fuel_stops': fuel_stops,
        'num_stops': num_stops,
        'estimated_cost_usd': round(cost, 2),
        'warning': warning
    }
