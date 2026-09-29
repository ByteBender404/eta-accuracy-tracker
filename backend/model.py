import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import json

from pipeline import preprocess_pipeline
from baseline import add_baseline_eta
from metrics import compare_models

def train_and_evaluate(data_path="data/train_full.csv", model_save_path="ml_model.pkl", metrics_save_path="metrics.json"):
    print("Loading and preprocessing data...")
    df = preprocess_pipeline(data_path)
    df = add_baseline_eta(df)
    
    # Target
    target = 'Time_taken(min)'
    
    # Features
    numerical_features = ['Distance_km', 'Delivery_person_Age', 'Delivery_person_Ratings', 'multiple_deliveries']
    categorical_features = ['Weatherconditions', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'Festival', 'City']
    
    # Make sure we only use columns that exist
    features = []
    for col in numerical_features + categorical_features:
        if col in df.columns:
            features.append(col)
            if col in numerical_features:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
    X = df[features]
    y = df[target]
    baseline_y = df['Promised_ETA_min']
    
    # Train-test split
    # We also need to split the baseline predictions to compare on the test set
    X_train, X_test, y_train, y_test, base_train, base_test = train_test_split(
        X, y, baseline_y, test_size=0.2, random_state=42
    )
    
    # Separate existing numerical/categorical based on what is in 'features'
    num_cols = [c for c in numerical_features if c in features]
    cat_cols = [c for c in categorical_features if c in features]
    
    # Preprocessor
    
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ])
    
    # Model pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', GradientBoostingRegressor(n_estimators=100, random_state=42))
    ])
    
    print("Training ML model...")
    model.fit(X_train, y_train)
    
    print("Evaluating models...")
    ml_test_pred = model.predict(X_test)
    
    comparison = compare_models(y_test.values, base_test.values, ml_test_pred)
    
    print("\n--- Evaluation Results ---")
    print("Baseline:", comparison['Baseline'])
    print("ML Model:", comparison['ML_Model'])
    print("Improvement:", comparison['Improvement'])
    
    # Save model and metrics
    joblib.dump(model, model_save_path)
    
    # Convert np floats to standard float for JSON
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(v) for v in obj]
        elif isinstance(obj, np.generic):
            return obj.item()
        else:
            return obj
            
    with open(metrics_save_path, "w") as f:
        json.dump(convert_types(comparison), f, indent=4)
        
    print(f"\nSaved model to {model_save_path} and metrics to {metrics_save_path}")
    
    return model, comparison

if __name__ == "__main__":
    train_and_evaluate()
