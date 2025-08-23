"""
Module to test routing logic.
Author: Ross Cochrane
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from flask import Flask, json
from routes.routing import routing_bp



class TestGenerateRoute(unittest.TestCase):
    """Unit tests for the generate_route endpoint in routing.py"""

    def setUp(self):
        """Set up a Flask test client and register the routing blueprint"""
        self.app = Flask(__name__)
        self.app.register_blueprint(routing_bp)
        self.client = self.app.test_client()

        self.valid_payload = {
            "start": [8.681495, 49.41461],
            "end": [8.687872, 49.420318],
            "mode": "foot-walking",
            "pollutant": "pm25"
        }

    @patch("routes.routing.openrouteservice.Client")
    @patch("routes.routing.enrich_route_with_pollution")
    def test_generate_route_success(self, mock_enrich, mock_ors_client):
        """Test successful route generation and pollution enrichment"""

        
        mock_base_route = {
            "features": [{
                "geometry": {
                    "coordinates": [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
                },
                "properties": {
                    "pollution_scores": [10, 20, 30]
                }
            }]
        }

        mock_enrich.return_value = mock_base_route
        mock_client_instance = MagicMock()
        mock_client_instance.directions.return_value = mock_base_route
        mock_ors_client.return_value = mock_client_instance

        response = self.client.post(
            "/routing/route",
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("features", data)
        self.assertIn("average_pollution_score", data["features"][0]["properties"])
        self.assertEqual(data["features"][0]["properties"]["average_pollution_score"], 20.0)

    def test_missing_fields(self):
        """Test request with missing required fields"""
        incomplete_payload = {
            "start": [8.681495, 49.41461],
            "mode": "foot-walking"
        }

        response = self.client.post(
            "/routing/route",
            data=json.dumps(incomplete_payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("routes.routing.openrouteservice.Client")
    def test_short_base_route(self, mock_ors_client):
        """Test handling of base route with too few coordinates"""
        short_route = {
            "features": [{
                "geometry": {
                    "coordinates": [[1, 1], [2, 2]]
                },
                "properties": {
                    "pollution_scores": [10, 20]
                }
            }]
        }

        mock_client_instance = MagicMock()
        mock_client_instance.directions.return_value = short_route
        mock_ors_client.return_value = mock_client_instance

        with patch("routes.routing.enrich_route_with_pollution", return_value=short_route):
            response = self.client.post(
                "/routing/route",
                data=json.dumps(self.valid_payload),
                content_type="application/json"
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("routes.routing.openrouteservice.Client")
    def test_ors_api_error(self, mock_ors_client):
        """Test handling of ORS API error"""
        from openrouteservice.exceptions import ApiError  

        mock_client_instance = MagicMock()
        mock_client_instance.directions.side_effect = ApiError("API error")  
        mock_ors_client.return_value = mock_client_instance

        response = self.client.post(
            "/routing/route",
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.get_json())

if __name__ == "__main__":
    unittest.main()