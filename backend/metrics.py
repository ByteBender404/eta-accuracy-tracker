from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import numpy as np
import pandas as pd

def calculate_metrics(y_true, y_pred):
    """
    Computes MAE, RMSE, MAPE, and % of orders within +/- 5 minutes.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    
    # Accuracy within 5 min
    errors = np.abs(y_true - y_pred)
    within_5_min = (errors <= 5).mean() * 100
    
    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
        "Within_5_min_pct": round(within_5_min, 2)
    }

def compare_models(y_true, baseline_pred, ml_pred):
    baseline_metrics = calculate_metrics(y_true, baseline_pred)
    ml_metrics = calculate_metrics(y_true, ml_pred)
    
    improvement = {
        "MAE_improvement_pct": round(((baseline_metrics['MAE'] - ml_metrics['MAE']) / baseline_metrics['MAE']) * 100, 2),
        "RMSE_improvement_pct": round(((baseline_metrics['RMSE'] - ml_metrics['RMSE']) / baseline_metrics['RMSE']) * 100, 2)
    }
    
    return {
        "Baseline": baseline_metrics,
        "ML_Model": ml_metrics,
        "Improvement": improvement
    }
