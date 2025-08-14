from flask import Flask
import unittest
from unittest.mock import patch, MagicMock
import math
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from utils.routes.enrichment import enrich_route_with_pollution

class TestEnrichRouteWithPollution(unittest.TestCase):
    """Unit tests for enrich_route_with_pollution function"""

    def setUp(self):
        """Set up a sample GeoJSON route with coordinates"""
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()

       
        self.route_geojson = {
            "features": [{
                "geometry": {
                    "coordinates": [
                        [8.681495, 49.41461],
                        [8.682, 49.415],
                        [8.683, 49.416]
                    ]
                },
                "properties": {}
            }]
        }

    @patch("utils.routes.enrichment.compute_aqi")
    @patch("utils.routes.enrichment.PollutionReading.query")
    def test_enrichment_with_valid_readings(self, mock_query, mock_compute_aqi):
        """Test enrichment when pollution readings are found for all coordinates"""

        # Mock reading object and AQI computation
        mock_reading = MagicMock()
        mock_query.join.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            mock_reading, mock_reading, mock_reading
        ]
        mock_compute_aqi.return_value = 5.0

        enriched = enrich_route_with_pollution(self.route_geojson.copy(), "aqi")

        scores = enriched["features"][0]["properties"]["pollution_scores"]
        avg = enriched["features"][0]["properties"]["average_pollution_score"]

        self.assertEqual(scores, [5.0, 5.0, 5.0])
        self.assertEqual(avg, 5.0)

    @patch("utils.routes.enrichment.compute_aqi")
    @patch("utils.routes.enrichment.PollutionReading.query")
    def test_enrichment_with_missing_readings(self, mock_query, mock_compute_aqi):
        """Test enrichment when no pollution readings are found"""

        mock_query.join.return_value.filter.return_value.order_by.return_value.first.return_value = None

        enriched = enrich_route_with_pollution(self.route_geojson.copy(), "co")

        scores = enriched["features"][0]["properties"]["pollution_scores"]
        avg = enriched["features"][0]["properties"]["average_pollution_score"]

        self.assertEqual(scores, [None, None, None])
        self.assertIsNone(avg)

    @patch("utils.routes.enrichment.compute_aqi")
    @patch("utils.routes.enrichment.PollutionReading.query")
    def test_enrichment_with_invalid_scores(self, mock_query, mock_compute_aqi):
        """Test enrichment when AQI returns None or inf"""

        mock_reading = MagicMock()
        mock_query.join.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            mock_reading, mock_reading, mock_reading
        ]
        mock_compute_aqi.side_effect = [None, float("inf"), 7.0]

        enriched = enrich_route_with_pollution(self.route_geojson.copy(), "aqi")

        scores = enriched["features"][0]["properties"]["pollution_scores"]
        avg = enriched["features"][0]["properties"]["average_pollution_score"]

        self.assertEqual(scores, [None, None, 7.0])
        self.assertEqual(avg, 7.0)

if __name__ == "__main__":
    unittest.main()