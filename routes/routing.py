from flask import Blueprint, request, jsonify
import openrouteservice
from models.site import Site
from models.pollution_reading import PollutionReading
from utils.pollution.aqi import compute_aqi
from utils.routes.enrichment import enrich_route_with_pollution

routing_bp = Blueprint('routing', __name__)

@routing_bp.route('/routing/route', methods=['POST'])  
def generate_route():
    """
    Generate a base route, then simulate 3 alternatives by inserting offset waypoints
    at ¼, ½, and ¾ of the base route. Each route is enriched with pollution data.
    The cleanest route is returned.
    """
    data = request.get_json()
    required_keys = {'start', 'end', 'mode', 'pollutant'}
    if not data or not required_keys.issubset(data):
        return jsonify({'error': 'Missing required input fields'}), 400

    start = data['start']
    end = data['end']
    mode = data['mode']
    pollutant = data['pollutant']

    def offset(coord, dx, dy):
        """Offset a coordinate by dx/dy degrees (~meters)."""
        return [coord[0] + dx, coord[1] + dy]

    # Initialize ORS client
    client = openrouteservice.Client(key='eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImI3MDVjODMxNDkyNzQ4NDE5MjBhNWQ0YmEyNTUxNmNlIiwiaCI6Im11cm11cjY0In0=')

    enriched_routes = []

    # Step 1: Request base route
    try:
        base_route = client.directions(
            coordinates=[start, end],
            profile=mode,
            format='geojson'
        )
        enriched_base = enrich_route_with_pollution(base_route, pollutant)
        enriched_routes.append(enriched_base)

    except openrouteservice.exceptions.ApiError as e:
        return jsonify({'error': f'ORS API error: {str(e)}'}), 502

    # Step 2: Extract base route coordinates
    coords = base_route['features'][0]['geometry']['coordinates']
    if len(coords) < 4:
        return jsonify({'error': 'Base route too short to extract waypoints'}), 400

    # Step 3: Define offset waypoints
    wp1 = offset(coords[len(coords) // 4], 0.0003, 0.0002)  # ~20–50m
    wp2 = offset(coords[len(coords) // 2], 0.0007, 0.0005)  # ~50–70m
    wp3 = offset(coords[3 * len(coords) // 4], 0.0002, 0.0001)  # ~20–30m

    waypoints = [wp1, wp2, wp3]

    # Step 4: Request 3 alternative routes with waypoints
    for wp in waypoints:
        try:
            route = client.directions(
                coordinates=[start, wp, end],
                profile=mode,
                format='geojson'
            )
            enriched = enrich_route_with_pollution(route, pollutant)
            enriched_routes.append(enriched)

        except openrouteservice.exceptions.ApiError:
            continue  # Skip failed variants

    def average_pollution_score(route_geojson):
        """Compute average pollution score for a route."""
        scores = route_geojson['features'][0]['properties']['pollution_scores']
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else float('inf')

    # Step 5: Select cleanest route
    best_route = min(enriched_routes, key=average_pollution_score)
    avg_score = average_pollution_score(best_route)
    best_route['features'][0]['properties']['average_pollution_score'] = round(avg_score, 2)

    return jsonify(best_route), 200
