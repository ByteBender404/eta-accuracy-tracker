import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from pipeline import preprocess_pipeline

# 1. Load Data just like model.py
df = preprocess_pipeline("data/train_full.csv")
target = 'Time_taken(min)'
df = df.dropna(subset=[target])

# Features setup
numerical_features = ['Distance_km', 'Delivery_person_Age', 'Delivery_person_Ratings', 'multiple_deliveries']
categorical_features = ['Weatherconditions', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival', 'City']

features = []
for col in numerical_features + categorical_features:
    if col in df.columns:
        features.append(col)
        if col in numerical_features:
            df[col] = pd.to_numeric(df[col], errors='coerce')

X = df[features]
y = df[target]

# Same split as model.py
X_train, X_test, y_test_actual, y_test_dummy = train_test_split(X, y, test_size=0.2, random_state=42)
# Wait, train_test_split returns X_train, X_test, y_train, y_test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load Model
model = joblib.load("ml_model.pkl")

# Get Predictions
y_pred = model.predict(X_test)

# Print Actual Stats
print("=== ACTUAL Time_taken(min) in Test Set ===")
print(f"Count: {len(y_test)}")
print(f"Min: {y_test.min():.2f}")
print(f"Max: {y_test.max():.2f}")
print(f"5th %: {y_test.quantile(0.05):.2f}")
print(f"25th %: {y_test.quantile(0.25):.2f}")
print(f"50th % (Median): {y_test.quantile(0.50):.2f}")
print(f"75th %: {y_test.quantile(0.75):.2f}")
print(f"95th %: {y_test.quantile(0.95):.2f}")

# Print Predicted Stats
print("\n=== ML MODEL PREDICTIONS on Test Set ===")
y_pred_series = pd.Series(y_pred)
print(f"Min: {y_pred_series.min():.2f}")
print(f"Max: {y_pred_series.max():.2f}")
print(f"5th %: {y_pred_series.quantile(0.05):.2f}")
print(f"25th %: {y_pred_series.quantile(0.25):.2f}")
print(f"50th %: {y_pred_series.quantile(0.50):.2f}")
print(f"75th %: {y_pred_series.quantile(0.75):.2f}")
print(f"95th %: {y_pred_series.quantile(0.95):.2f}")
