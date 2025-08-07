from flask import Blueprint, jsonify
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_
from extensions import db
from models.site import Site
from models.pollution_reading import PollutionReading

heatmap_bp = Blueprint('heatmap', __name__, url_prefix='/heatmap')

@heatmap_bp.route('/latest_readings', methods=['GET'])
def get_latest_readings():
    """
    Retrieves the latest pollution from each site.
    """
    subquery = db.session.query(
        PollutionReading.system_code_number,
        func.max(PollutionReading.last_updated).label('latest')
    ).group_by(PollutionReading.system_code_number).subquery()

    ReadingAlias = aliased(PollutionReading)

    results = db.session.query(
        Site.system_code_number,
        Site.latitude,
        Site.longitude,
        ReadingAlias.co,
        ReadingAlias.no,
        ReadingAlias.no2,
        ReadingAlias.noise,
        ReadingAlias.last_updated
    ).join(
        subquery,
        Site.system_code_number == subquery.c.system_code_number
    ).join(
        ReadingAlias,
        and_(
            Site.system_code_number == ReadingAlias.system_code_number,
            ReadingAlias.last_updated == subquery.c.latest
        )
    ).all()

    response = []
    for row in results:
        response.append({
            'systemCodeNumber': row.system_code_number,
            'latitude': row.latitude,
            'longitude': row.longitude,
            'readings': {
                'co': row.co,
                'no': row.no,
                'no2': row.no2,
                'noise': row.noise,
                'lastUpdated': row.last_updated.isoformat()
            }
        })

    return jsonify(response)