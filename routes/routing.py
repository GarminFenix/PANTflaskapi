"""
Provides a Flask Blueprint for generating and evaluating routes based on pollution data.
Uses OpenRouteService to generate a base route and three alternatives by inserting offset waypoints.
Each route is enriched with pollution metrics, and the cleanest route is returned as GeoJSON.
"""

from flask import Blueprint, request, jsonify
import openrouteservice
import math
import os

from utils.pollution.aqi import compute_aqi
from utils.routes.enrichment import enrich_route_with_pollution

routing_bp = Blueprint('routing', __name__)

@routing_bp.route('/routing/route', methods=['POST'])  
def generate_route():
    """
    Generate a base route, then simulate 3 alternatives by inserting offset waypoints
    at ¼, ½, and ¾ of the base route. Each route is enriched with pollution data.
    The cleanest route is returned as a GEOJson
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
    ors_key = os.getenv('ORS_API_KEY')
    if not ors_key:
        print("Error: ORS_API_KEY environment not set.")
        
    client = openrouteservice.Client(key=os.getenv('ORS_API_KEY'))

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

    # Prevent an infinite being returned
    if math.isinf(avg_score) or math.isnan(avg_score):
        avg_score_json = None
    else:
        avg_score_json = round(avg_score, 2)

    # debuggin
    print('Pollution scores:', best_route['features'][0]['properties']['pollution_scores'])
    print('Average pollution score:', avg_score_json)

    best_route['features'][0]['properties']['average_pollution_score'] = avg_score_json

    return jsonify(best_route), 200
