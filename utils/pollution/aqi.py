"""
Utility functions for computing AQI (Air Quality Index) based on pollutant readings.
Pollutants are normalised 0-10.0 based on simulated ranges.
Author: Ross Cochrane
"""

def normalise_co(co):
    """
    Normalise CO level (in ppm) to a scale of 0–10.0.
    Based on simulated range: 0.1–5.0 ppm.
    """
    if co is None:
        return 0
    co = max(0.1, min(co, 5.0))  
    return round((co - 0.1) / (5.0 - 0.1) * 10.0, 2)


def normalise_no(no):
    """
    Normalise NO (ppb) to a scale of 0–10.0.
    Based on simulated range: 1–150 ppb.
    """
    if no is None:
        return 0.0
    no = max(1, min(no, 150)) 
    return round((no - 1) / (150 - 1) * 10.0, 2)


def normalise_no2(no2):
    """
    Normalize NO₂ (ppb) to a scale of 0–10.0.
    Based on simulated range: 5–300 ppb.
    """
    if no2 is None:
        return 0.0
    no2 = max(5, min(no2, 300))  
    return round((no2 - 5) / (300 - 5) * 10.0, 2)

    
def normalise_noise(noise_db):
    """
    Normalize noise (dB) to a scale of 0–10.0.
    Based on simulated range: 30–100 dB.
    """
    if noise_db is None:
        return 0.0
    noise_db = max(30, min(noise_db, 100))  
    return round((noise_db - 30) / (100 - 30) * 10.0, 2)

def compute_custom_aqi(reading):
    """
    Compute a custom AQI based on CO, NO, and NO2 readings.
    """
    co_index = normalise_co(reading.co)
    no2_index = normalise_no2(reading.no2)
    no_index = normalise_no(reading.no)  

    return max(co_index, no_index, no2_index)  # EPA weighting where worst pollutant has heaviest weighting

def compute_aqi(reading, pollutant):
    """
    Returns either normalised reading for a specific pollutant or the custom AQI based on all air pollutants.
    """
    if pollutant.lower() == 'aqi':
        return compute_custom_aqi(reading)
    elif pollutant.lower() == 'co':
        return normalise_co(reading.co)
    elif pollutant.lower() == 'no':
        return normalise_no2(reading.no)  
    elif pollutant.lower() == 'no2':
        return normalise_no2(reading.no2)
    elif pollutant.lower() == 'noise':
        return normalise_noise(reading.noise)
    else:
        return None
