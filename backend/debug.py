import pandas as pd
from pipeline import preprocess_pipeline

df = preprocess_pipeline("e:/PROJECT/9/eta_tracker/backend/data/train.csv")
print("Max distance:", df['Distance_km'].max())
print("Min distance:", df['Distance_km'].min())
outliers = df[df['Distance_km'] > 100]
print(f"Number of rows with distance > 100km: {len(outliers)}")
print("Sample outliers:\n", outliers[['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude', 'Distance_km']].head())
