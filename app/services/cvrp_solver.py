from typing import List, Dict, Any, Tuple
from app.services.distance_matrix import build_distance_matrix, haversine_distance, fetch_road_route_geometry

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    HAS_OR_TOOLS = True
except ImportError:
    HAS_OR_TOOLS = False

async def solve_cvrp(
    depot_location: Tuple[float, float],
    bin_locations: List[Tuple[float, float]],
    demands: List[int],
    vehicle_capacities: List[int],
    vehicle_ids: List[int]
) -> Dict[str, Any]:
    """
    Solves Capacitated Vehicle Routing Problem (CVRP).
    Uses Google OR-Tools if available; falls back to Nearest-Neighbor routing algorithm.
    Fetches real road-following geometry (streets/turns) from OSRM for each route.
    """
    if not bin_locations or not vehicle_capacities:
        return {"success": False, "message": "No bins or vehicles available for routing.", "routes": {}}

    if HAS_OR_TOOLS:
        res = await _solve_with_ortools(depot_location, bin_locations, demands, vehicle_capacities, vehicle_ids)
    else:
        res = await _solve_nearest_neighbor(depot_location, bin_locations, demands, vehicle_capacities, vehicle_ids)

    # Enhance every route with real road turn-by-turn geometry
    if res.get("success") and "routes" in res:
        for v_id, route_data in res["routes"].items():
            if isinstance(route_data, dict) and "waypoints" in route_data:
                coords = [(wp["latitude"], wp["longitude"]) for wp in route_data["waypoints"]]
                road_geometry = await fetch_road_route_geometry(coords)
                route_data["road_geometry"] = road_geometry
            elif isinstance(route_data, list):
                coords = [(wp["latitude"], wp["longitude"]) for wp in route_data]
                road_geometry = await fetch_road_route_geometry(coords)
                res["routes"][v_id] = {
                    "waypoints": route_data,
                    "road_geometry": road_geometry
                }

    return res

async def _solve_with_ortools(
    depot_location: Tuple[float, float],
    bin_locations: List[Tuple[float, float]],
    demands: List[int],
    vehicle_capacities: List[int],
    vehicle_ids: List[int]
) -> Dict[str, Any]:
    all_locations = [depot_location] + bin_locations
    all_demands = [0] + demands

    distance_matrix = await build_distance_matrix(all_locations)
    num_vehicles = len(vehicle_capacities)
    depot_index = 0

    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return all_demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, vehicle_capacities, True, "Capacity"
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return {"success": False, "message": "Could not find a feasible OR-Tools route.", "routes": {}}

    result_routes = {}
    for vehicle_idx in range(num_vehicles):
        v_id = vehicle_ids[vehicle_idx]
        index = routing.Start(vehicle_idx)
        route_nodes = []
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            loc = all_locations[node]
            route_nodes.append({
                "node_index": node,
                "latitude": loc[0],
                "longitude": loc[1],
                "is_depot": (node == 0)
            })
            index = solution.Value(routing.NextVar(index))

        end_node = manager.IndexToNode(index)
        end_loc = all_locations[end_node]
        route_nodes.append({
            "node_index": end_node,
            "latitude": end_loc[0],
            "longitude": end_loc[1],
            "is_depot": True
        })
        result_routes[v_id] = {
            "waypoints": route_nodes
        }

    return {"success": True, "message": "Routes generated via Google OR-Tools.", "routes": result_routes}

async def _solve_nearest_neighbor(
    depot_location: Tuple[float, float],
    bin_locations: List[Tuple[float, float]],
    demands: List[int],
    vehicle_capacities: List[int],
    vehicle_ids: List[int]
) -> Dict[str, Any]:
    """Fallback Greedy Nearest-Neighbor CVRP solver when OR-Tools is uninstalled."""
    unvisited = list(range(len(bin_locations)))
    result_routes = {}

    for idx, v_id in enumerate(vehicle_ids):
        cap_remaining = vehicle_capacities[idx]
        current_loc = depot_location
        route_nodes = [{"node_index": 0, "latitude": depot_location[0], "longitude": depot_location[1], "is_depot": True}]

        while unvisited:
            best_bin_idx = None
            best_dist = float('inf')

            for b_i in unvisited:
                demand = demands[b_i]
                if demand <= cap_remaining:
                    dist = haversine_distance(current_loc, bin_locations[b_i])
                    if dist < best_dist:
                        best_dist = dist
                        best_bin_idx = b_i

            if best_bin_idx is None:
                break

            unvisited.remove(best_bin_idx)
            cap_remaining -= demands[best_bin_idx]
            current_loc = bin_locations[best_bin_idx]
            route_nodes.append({
                "node_index": best_bin_idx + 1,
                "latitude": current_loc[0],
                "longitude": current_loc[1],
                "is_depot": False
            })

        route_nodes.append({"node_index": 0, "latitude": depot_location[0], "longitude": depot_location[1], "is_depot": True})
        result_routes[v_id] = {
            "waypoints": route_nodes
        }

    return {"success": True, "message": "Routes generated via Nearest-Neighbor heuristic.", "routes": result_routes}
