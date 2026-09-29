from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import json
import pandas as pd
import numpy as np

from pipeline import preprocess_pipeline
from baseline import calculate_baseline_eta
from metrics import calculate_metrics

app = FastAPI(title="ETA Tracker API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global assets
model = None
metrics_summary = {}
df_eval = None

class PredictionRequest(BaseModel):
    Distance_km: float
    Road_traffic_density: str
    Weatherconditions: str
    Type_of_vehicle: str
    multiple_deliveries: float = 0.0
    Delivery_person_Age: float = 30.0
    Delivery_person_Ratings: float = 4.5
    Festival: str = "No"
    City: str = "Metropolitian"
    Type_of_order: str = "Snack"

@app.on_event("startup")
def startup_event():
    global model, metrics_summary, df_eval
    
    print("Loading ML model...")
    model = joblib.load("ml_model.pkl")
    
    print("Loading metrics summary...")
    with open("metrics.json", "r") as f:
        metrics_summary = json.load(f)
        
    print("Loading dataset for breakdown analysis...")
    # Load dataset to serve breakdowns and sample predictions fast
    try:
        df = preprocess_pipeline("data/train_full.csv")
        # Ensure we only work with rows that have actual time for evaluation
        df = df.dropna(subset=['Time_taken(min)'])
        
        # Calculate Baseline
        df['Promised_ETA_min'] = df.apply(calculate_baseline_eta, axis=1)
        
        # Calculate ML Model predictions
        # We need to make sure we pass the exact columns the model expects
        df['ML_Prediction'] = model.predict(df)
        
        df_eval = df
        print(f"Loaded evaluation dataset with {len(df_eval)} rows.")
    except Exception as e:
        print(f"Warning: Could not load dataset for evaluation. {e}")

@app.get("/api/summary")
def get_summary():
    return metrics_summary

@app.get("/api/breakdown")
def get_breakdown(by: str):
    if df_eval is None:
        raise HTTPException(status_code=500, detail="Evaluation dataset not loaded")
        
    valid_dimensions = ['City', 'Weatherconditions', 'Road_traffic_density', 'Type_of_vehicle', 'Festival']
    if by not in valid_dimensions:
        raise HTTPException(status_code=400, detail=f"Invalid breakdown dimension. Must be one of {valid_dimensions}")
        
    breakdown_results = []
    
    for name, group in df_eval.groupby(by):
        if len(group) < 10:  # Skip tiny segments
            continue
            
        y_true = group['Time_taken(min)'].values
        base_pred = group['Promised_ETA_min'].values
        ml_pred = group['ML_Prediction'].values
        
        base_metrics = calculate_metrics(y_true, base_pred)
        ml_metrics = calculate_metrics(y_true, ml_pred)
        
        breakdown_results.append({
            "segment": str(name),
            "count": len(group),
            "baseline": base_metrics,
            "ml_model": ml_metrics
        })
        
    return breakdown_results

@app.get("/api/sample-predictions")
def get_sample_predictions(n: int = 50):
    if df_eval is None:
        raise HTTPException(status_code=500, detail="Evaluation dataset not loaded")
        
    sample = df_eval.sample(n=min(n, len(df_eval)), random_state=42)
    
    results = []
    for _, row in sample.iterrows():
        actual = row['Time_taken(min)']
        base_pred = row['Promised_ETA_min']
        ml_pred = round(row['ML_Prediction'])
        
        results.append({
            "ID": str(row.get('ID', 'Unknown')),
            "actual_time": actual,
            "baseline_eta": base_pred,
            "ml_eta": ml_pred,
            "baseline_error": abs(actual - base_pred),
            "ml_error": abs(actual - ml_pred),
            "Distance_km": round(row['Distance_km'], 2),
            "Weatherconditions": row.get('Weatherconditions', ''),
            "Road_traffic_density": row.get('Road_traffic_density', '')
        })
        
    return results

@app.post("/api/predict")
def predict_eta(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    # Create single-row dataframe for prediction
    input_data = request.dict()
    df_input = pd.DataFrame([input_data])
    
    # Calculate baseline using the same formula
    baseline_eta = calculate_baseline_eta(df_input.iloc[0])
    
    # Calculate ML prediction
    # The pipeline handles scaling and OHE, so we just pass the DataFrame
    try:
        ml_pred_raw = model.predict(df_input)[0]
        ml_eta = round(ml_pred_raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
    return {
        "baseline_eta": baseline_eta,
        "ml_eta": ml_eta,
        "raw_ml_prediction": ml_pred_raw
    }
