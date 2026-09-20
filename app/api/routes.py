import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.bin import Bin, BinStatus
from app.models.vehicle import Vehicle
from app.models.depot import Depot
from app.models.route import Route
from app.services.cvrp_solver import solve_cvrp

router = APIRouter(prefix="/routes", tags=["Route Optimization & Maps"])

@router.get("/search-location")
async def search_location(q: str = Query(..., min_length=1)):
    """Server-side geocoding proxy to Nominatim to bypass browser CORS & Ad-blockers."""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={httpx.URL(q).raw_path.decode() if hasattr(httpx.URL(q), 'raw_path') else q}&addressdetails=1&limit=5"
    headers = {"User-Agent": "GarbageTruckMonitoringSystem/2.0 (wastetrack@demo.org)"}
    try:
        async with httpx.AsyncClient(timeout=6.0, headers=headers) as client:
            resp = await client.get(f"https://nominatim.openstreetmap.org/search?format=json&q={q}&limit=5")
            if resp.status_code == 200:
                return resp.json()
            return []
    except Exception as e:
        print(f"[Geocoding Proxy Error]: {e}")
        return []

@router.post("/generate")
async def generate_routes(db: AsyncSession = Depends(get_db)):
    # 1. Fetch Depot location
    depot_res = await db.execute(select(Depot))
    depots = depot_res.scalars().all()
    if not depots:
        # Default depot coordinates: VIT Chennai
        depot_location = (12.8406, 80.1534)
    else:
        depot_location = (depots[0].latitude, depots[0].longitude)

    # 2. Fetch Bins (Focus on Overfilled and Normal bins needing collection)
    bins_res = await db.execute(select(Bin))
    all_bins = bins_res.scalars().all()
    
    # Filter bins with > 20% capacity
    target_bins = [b for b in all_bins if b.fill_percentage > 20.0]
    if not target_bins:
        target_bins = all_bins

    if not target_bins:
        raise HTTPException(status_code=400, detail="No bins found in database to generate routes.")

    bin_locations = [(b.latitude, b.longitude) for b in target_bins]
    demands = [int(b.capacity * (b.fill_percentage / 100.0)) for b in target_bins]

    # 3. Fetch Vehicles
    veh_res = await db.execute(select(Vehicle))
    vehicles = veh_res.scalars().all()
    if not vehicles:
        raise HTTPException(status_code=400, detail="No vehicles available. Add at least one vehicle.")

    vehicle_capacities = [int(v.capacity) for v in vehicles]
    vehicle_ids = [v.id for v in vehicles]

    # 4. Solve CVRP
    solution = await solve_cvrp(
        depot_location=depot_location,
        bin_locations=bin_locations,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        vehicle_ids=vehicle_ids
    )

    if not solution["success"]:
        raise HTTPException(status_code=400, detail=solution["message"])

    # 5. Persist generated routes into DB
    saved_routes = []
    for v_id, route_data in solution["routes"].items():
        waypoints = route_data.get("waypoints", []) if isinstance(route_data, dict) else route_data
        route_obj = Route(vehicle_id=v_id, waypoints=waypoints)
        db.add(route_obj)
        saved_routes.append({"vehicle_id": v_id, "waypoints": waypoints})
    
    await db.commit()

    return {
        "status": "success",
        "depot": {"latitude": depot_location[0], "longitude": depot_location[1]},
        "routes": solution["routes"]
    }

@router.get("/latest")
async def get_latest_routes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Route).order_by(Route.generated_at.desc()).limit(10))
    routes = result.scalars().all()
    return routes
