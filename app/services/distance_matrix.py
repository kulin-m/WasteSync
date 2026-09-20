import math
import httpx
from typing import List, Tuple
from app.config import settings

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> int:
    """
    Calculate Haversine distance in meters between two (lat, lon) points.
    100% offline, zero-cost fallback.
    """
    R = 6371000  # Radius of Earth in meters
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return int(R * c)

async def build_distance_matrix(coordinates: List[Tuple[float, float]]) -> List[List[int]]:
    """
    Build a distance matrix (in meters) for a list of (latitude, longitude) tuples.
    Tries OSRM free public server first; falls back to Haversine calculation.
    """
    num_coords = len(coordinates)
    if num_coords == 0:
        return []

    # 1. Try OSRM Free API if server configured
    if settings.OSRM_SERVER_URL:
        try:
            # OSRM format: lon,lat;lon,lat...
            coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{settings.OSRM_SERVER_URL.rstrip('/')}/table/v1/driving/{coord_str}?annotations=distance"
            
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    if "distances" in data:
                        matrix = [[int(dist) if dist is not None else 0 for dist in row] for row in data["distances"]]
                        return matrix
        except Exception as e:
            print(f"[Distance Matrix] OSRM call failed, falling back to Haversine: {e}")

    # 2. Offline Haversine Fallback (Zero-cost, fast)
    matrix = []
    for i in range(num_coords):
        row = []
        for j in range(num_coords):
            if i == j:
                row.append(0)
            else:
                row.append(haversine_distance(coordinates[i], coordinates[j]))
        matrix.append(row)

    return matrix

async def fetch_road_route_geometry(coordinates: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Fetches the exact turn-by-turn road-following coordinates geometry from OSRM Route API.
    Returns a list of [latitude, longitude] points following real roads/streets,
    ensuring each stop is seamlessly connected.
    """
    if len(coordinates) < 2:
        return [[lat, lon] for lat, lon in coordinates]

    if settings.OSRM_SERVER_URL:
        try:
            # OSRM expects: lon,lat;lon,lat;...
            coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{settings.OSRM_SERVER_URL.rstrip('/')}/route/v1/driving/{coord_str}?overview=full&geometries=geojson&radiuses={';'.join(['1000' for _ in coordinates])}"

            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    if "routes" in data and len(data["routes"]) > 0:
                        geo_coords = data["routes"][0]["geometry"]["coordinates"]
                        # GeoJSON coordinates are [lon, lat], convert to Leaflet [lat, lon]
                        road_points = [[pt[1], pt[0]] for pt in geo_coords]
                        
                        # Ensure the path begins at start coord and ends at final coord
                        if road_points:
                            if [coordinates[0][0], coordinates[0][1]] != road_points[0]:
                                road_points.insert(0, [coordinates[0][0], coordinates[0][1]])
                            if [coordinates[-1][0], coordinates[-1][1]] != road_points[-1]:
                                road_points.append([coordinates[-1][0], coordinates[-1][1]])

                        return road_points
        except Exception as e:
            print(f"[Route Geometry] OSRM route geometry fetch failed: {e}")

    # Fallback to direct stop lines if OSRM is offline
    return [[lat, lon] for lat, lon in coordinates]
