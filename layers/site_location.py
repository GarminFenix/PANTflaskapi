from flask import Blueprint, jsonify
from models.site import Site
from extensions import db

# Define a new Blueprint for site-related routes
sites_bp = Blueprint('sites', __name__)


@sites_bp.route('/sites', methods=['GET'])
def get_all_sites():
    """
    Returns all monitoring sites from the database as GeoJSON.
    """
    
    all_sites = Site.query.all()

    # Build a GeoJSON FeatureCollection
    features = []
    for site in all_sites:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [site.longitude, site.latitude] # ie convert to long, lat
            },
            "properties": {
                "systemCodeNumber": site.system_code_number,
            }
        })

    # Wrap the list of features in a FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return jsonify(geojson), 200