"""
Unit tests for the heatmap blueprint routes.
This module tests the '/heatmap/latest_readings' endpoint to ensure it returns
the expected data structure and status code.
Author: Ross Cochrane
"""
import sys
import os

# Add the parent directory to sys.path so 'app' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import app
import pytest
import unittest
from app import app


class TestHeatmap(unittest.TestCase):
    """
    Test case for the heatmap routes.
    """

    def test_get_latest_readings(self):
        """
        Test the '/heatmap/latest_readings' endpoint.

        This test performs the following checks:
        - Confirms the response status code is 200 (OK)
        - Validates that the response is a list
        - If the list contains data, verifies the presence of expected keys:
          'systemCodeNumber', 'latitude', 'longitude', and 'readings'
        - Within 'readings', checks for keys: 'co', 'no', 'no2', 'noise', 'lastUpdated'
        """
        with app.test_client() as client:
            response = client.get('/heatmap/latest_readings')
            self.assertEqual(response.status_code, 200, "Expected status code 200")

            data = response.get_json()
            self.assertIsInstance(data, list, "Response should be a list")

            # Validate structure of the first item if data is present
            if data:
                site = data[0]
                self.assertIn('systemCodeNumber', site, "Missing 'systemCodeNumber'")
                self.assertIn('latitude', site, "Missing 'latitude'")
                self.assertIn('longitude', site, "Missing 'longitude'")
                self.assertIn('readings', site, "Missing 'readings'")

                readings = site['readings']
                for key in ['co', 'no', 'no2', 'noise', 'lastUpdated']:
                    self.assertIn(key, readings, f"Missing '{key}' in readings")


if __name__ == '__main__':
    unittest.main()
