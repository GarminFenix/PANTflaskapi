"""
Provides functionality to enrich a route GeoJSON with pollution data.
Author: Ross Cochrane
"""

from sqlalchemy.orm import joinedload
from geoalchemy2.functions import ST_Point, ST_DWithin, ST_SetSRID
from models.pollution_reading import PollutionReading
from models.site import Site
from utils.pollution.aqi import compute_aqi
import math


def enrich_route_with_pollution(route_geojson, pollutant):
    """
    For each coordinate in the route geometry:
    - Queries the database for the nearest pollution reading within 200m
    - Computes a score using either the selected pollutant or AQI
    - Appends the score to a list

    The resulting list of scores is attached to the route's GeoJSON properties
    under 'pollution_scores'.
    :param route_geojson: GeoJSON object returned by OpenRouteService
    :param pollutant: 'co', 'no', 'no2', 'noise', or 'aqi'
    :return: Enriched GeoJSON with pollution scores
    """

    coordinates = route_geojson['features'][0]['geometry']['coordinates']
    pollution_scores = []

    for lon, lat in coordinates:
        reading = PollutionReading.query.join(Site).filter(
            ST_DWithin(
                Site.location,
                ST_SetSRID(ST_Point(lon, lat), 4326),
                0.002  # 200m radius
            )
    ).order_by(PollutionReading.last_updated.desc()).first()

        if reading:
            score = compute_aqi(reading, pollutant)
            score = None if score is None or math.isinf(score) else score
        else:
            score = None

        pollution_scores.append(score)

    # Attach scores to route properties
    valid_scores = [s for s in pollution_scores if s is not None]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else None
    route_geojson['features'][0]['properties']['pollution_scores'] = pollution_scores
    route_geojson['features'][0]['properties']['average_pollution_score'] = avg_score
    return route_geojson