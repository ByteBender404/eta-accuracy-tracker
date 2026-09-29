import pandas as pd
import numpy as np
from geopy.distance import geodesic

def load_data(filepath="data/train_full.csv"):
    df = pd.read_csv(filepath, encoding='latin1')
    return df

def clean_data(df):
    # Basic cleaning
    # Remove rows with NaN in critical columns
    critical_cols_all = ['Restaurant_latitude', 'Restaurant_longitude', 
                     'Delivery_location_latitude', 'Delivery_location_longitude', 
                     'Time_taken(min)', 'Vehicle_condition', 'Type_of_vehicle']
    
    critical_cols = [c for c in critical_cols_all if c in df.columns]
    
    # Check if 'Time_taken(min)' has string format like '(min) 24'
    if df['Time_taken(min)'].dtype == object:
        df['Time_taken(min)'] = df['Time_taken(min)'].astype(str).str.extract(r'(\d+)').astype(float)
        
    initial_len = len(df)
    df = df.dropna(subset=critical_cols)
    print(f"Data cleaning: Dropped {initial_len - len(df)} rows with nulls in critical columns. Remaining: {len(df)}")
    return df

def calculate_distance(row):
    try:
        rest = (row['Restaurant_latitude'], row['Restaurant_longitude'])
        dest = (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
        # Distance in km
        return geodesic(rest, dest).kilometers
    except Exception:
        return 0.0

def engineer_features(df):
    df = df.copy()
    # Distance
    df['Distance_km'] = df.apply(calculate_distance, axis=1)
    
    # Filter out absurd distances (e.g. invalid lat/lon pairs)
    initial_len = len(df)
    df = df[df['Distance_km'] <= 50]
    print(f"Data cleaning: Dropped {initial_len - len(df)} rows with absurd Haversine distance (> 50km).")
    
    # Fill categorical features
    categorical_cols = ['Weatherconditions', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival', 'City']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown').astype(str).str.strip()
            
    return df

def preprocess_pipeline(filepath="data/train_full.csv"):
    df = load_data(filepath)
    df.columns = [c.strip() for c in df.columns]
    
    print("Initial Data Shape:", df.shape)
    print("Columns in dataset:", list(df.columns))
    
    if 'Weather_conditions' in df.columns:
        df = df.rename(columns={'Weather_conditions': 'Weatherconditions'})
        
    if 'Time_taken (min)' in df.columns:
        df = df.rename(columns={'Time_taken (min)': 'Time_taken(min)'})
    
    df = clean_data(df)
    df = engineer_features(df)
    return df

if __name__ == "__main__":
    df = preprocess_pipeline()
    print("Pipeline run successfully. Shape:", df.shape)
