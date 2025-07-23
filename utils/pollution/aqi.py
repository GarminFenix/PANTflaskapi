"""
Utility functions for computing AQI (Air Quality Index) based on pollutant readings
and EPA breakpoints.
"""

def normalize_co(co):
    """
    Normalize CO (Carbon Monoxide) reading to a scale of 0-500.
    """
    # Example: scale CO (ppm) to 0–500
    if co is None:
        return 0
    if co <= 4.4:
        return co / 4.4 * 50
    elif co <= 9.4:
        return 50 + (co - 4.4) / (9.4 - 4.4) * 50
    
    else:
        return 500

def normalize_no2(no2):
    """
    Normalize NO2 (Nitrogen Dioxide) reading to a scale of 0-500."""
    # Example: scale NO2 (ppb) to 0–500
    if no2 is None:
        return 0
    if no2 <= 53:
        return no2 / 53 * 50
    elif no2 <= 100:
        return 50 + (no2 - 53) / (100 - 53) * 50
    
    else:
        return 500

def compute_custom_aqi(reading):
    """
    Compute a custom AQI based on CO, NO, and NO2 readings.
    """
    co_index = normalize_co(reading.co)
    no2_index = normalize_no2(reading.no2)
    no_index = normalize_no2(reading.no)  # reuse NO2 scale if needed

    return max(co_index, no_index, no2_index)  # EPA weighting where worst pollutant dominates

def compute_aqi(reading, pollutant):
    """
    Returns either normalized AQI for a specific pollutant or a custom AQI based on multiple pollutants.
    """
    if pollutant == 'aqi':
        return compute_custom_aqi(reading)
    elif pollutant in ['co', 'no', 'no2']:
        return getattr(reading, pollutant, None)
    else:
        return None
