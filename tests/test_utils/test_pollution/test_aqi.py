import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from utils.pollution.aqi import (
    normalise_co,
    normalise_no,
    normalise_no2,
    normalise_noise,
    compute_custom_aqi,
    compute_aqi
)

import unittest

class MockReading:
    """Mock class to simulate pollutant readings"""
    def __init__(self, co=None, no=None, no2=None, noise=None):
        self.co = co
        self.no = no
        self.no2 = no2
        self.noise = noise

class TestAQIUtils(unittest.TestCase):
    """Unit tests for AQI normalization and computation functions"""

    def test_normalise_co(self):
        """Test CO normalization across range and edge cases"""
        self.assertEqual(normalise_co(None), 0)
        self.assertEqual(normalise_co(0.1), 0.0)
        self.assertEqual(normalise_co(5.0), 10.0)
        self.assertEqual(normalise_co(2.55), round((2.55 - 0.1) / (5.0 - 0.1) * 10.0, 2))
        self.assertEqual(normalise_co(0.0), 0.0)  # clamped to 0.1
        self.assertEqual(normalise_co(6.0), 10.0)  # clamped to 5.0

    def test_normalise_no(self):
        """Test NO normalization across range and edge cases"""
        self.assertEqual(normalise_no(None), 0.0)
        self.assertEqual(normalise_no(1), 0.0)
        self.assertEqual(normalise_no(150), 10.0)
        self.assertEqual(normalise_no(75), round((75 - 1) / (149) * 10.0, 2))
        self.assertEqual(normalise_no(0), 0.0)  # clamped to 1
        self.assertEqual(normalise_no(200), 10.0)  # clamped to 150

    def test_normalise_no2(self):
        """Test NO2 normalization across range and edge cases"""
        self.assertEqual(normalise_no2(None), 0.0)
        self.assertEqual(normalise_no2(5), 0.0)
        self.assertEqual(normalise_no2(300), 10.0)
        self.assertEqual(normalise_no2(150), round((150 - 5) / (295) * 10.0, 2))
        self.assertEqual(normalise_no2(0), 0.0)  # clamped to 5
        self.assertEqual(normalise_no2(400), 10.0)  # clamped to 300

    def test_normalise_noise(self):
        """Test noise normalization across range and edge cases"""
        self.assertEqual(normalise_noise(None), 0.0)
        self.assertEqual(normalise_noise(30), 0.0)
        self.assertEqual(normalise_noise(100), 10.0)
        self.assertEqual(normalise_noise(65), round((65 - 30) / 70 * 10.0, 2))
        self.assertEqual(normalise_noise(10), 0.0)  # clamped to 30
        self.assertEqual(normalise_noise(120), 10.0)  # clamped to 100

    def test_compute_custom_aqi(self):
        """Test custom AQI computation using worst pollutant"""
        reading = MockReading(co=2.0, no=100, no2=250)
        co_index = normalise_co(reading.co)
        no_index = normalise_no(reading.no)
        no2_index = normalise_no2(reading.no2)
        expected = max(co_index, no_index, no2_index)
        self.assertEqual(compute_custom_aqi(reading), expected)

    def test_compute_aqi_specific_pollutants(self):
        """Test compute_aqi for each pollutant type"""
        reading = MockReading(co=1.0, no=50, no2=100, noise=60)
        self.assertEqual(compute_aqi(reading, 'co'), normalise_co(reading.co))
        self.assertEqual(compute_aqi(reading, 'no'), normalise_no2(reading.no))  # Note: uses NO2 normalization
        self.assertEqual(compute_aqi(reading, 'no2'), normalise_no2(reading.no2))
        self.assertEqual(compute_aqi(reading, 'noise'), normalise_noise(reading.noise))
        self.assertEqual(compute_aqi(reading, 'aqi'), compute_custom_aqi(reading))

    def test_compute_aqi_invalid_pollutant(self):
        """Test compute_aqi with unsupported pollutant"""
        reading = MockReading(co=1.0, no=50, no2=100, noise=60)
        self.assertIsNone(compute_aqi(reading, 'ozone'))

if __name__ == "__main__":
    unittest.main()