import pandas as pd

def calculate_baseline_eta(row):
    """
    Naive baseline ETA formula:
    - Base distance calculation: Distance / Average Speed
    - Average speed mapped loosely from vehicle type (in km/hr)
    - Traffic offset mapped loosely from traffic density
    Returns ETA in minutes.
    """
    distance = row.get('Distance_km', 0)
    vehicle = str(row.get('Type_of_vehicle', '')).strip().lower()
    traffic = str(row.get('Road_traffic_density', '')).strip().lower()
    
    # Assume some basic speeds
    speed_map = {
        'motorcycle': 40,
        'scooter': 35,
        'electric scooter': 30,
        'bicycle': 15,
    }
    avg_speed = speed_map.get(vehicle, 35) # default 35 km/h
    
    # Base time in minutes
    base_time = (distance / avg_speed) * 60 if avg_speed > 0 else 0
    
    # Traffic delays in minutes
    traffic_delay_map = {
        'low': 2,
        'medium': 5,
        'high': 10,
        'jam': 20
    }
    traffic_delay = traffic_delay_map.get(traffic, 5) # default 5
    
    # Basic prep time
    prep_time = 10
    
    total_eta = base_time + traffic_delay + prep_time
    return round(total_eta)

def add_baseline_eta(df):
    df = df.copy()
    df['Promised_ETA_min'] = df.apply(calculate_baseline_eta, axis=1)
    return df
