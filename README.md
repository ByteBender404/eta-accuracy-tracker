# Public ETA Accuracy Tracker with ML Baseline

[![Live Demo](https://img.shields.io/badge/Live_Demo-Available-success.svg)](https://eta-accuracy-tracker-1.onrender.com)
*Hosted on a free tier, so the first load may take ~30-60 seconds while the server wakes up.*

Delivery ETA prediction accuracy is a critical metric for food delivery and logistics platforms like Swiggy, Zomato, and Delhivery. An inaccurate ETA directly degrades customer trust, user retention, and operational efficiency. This project is a full-stack tool that benchmarks delivery ETA prediction accuracy by comparing a simulated naive platform baseline against a custom-trained Machine Learning model. 

## Methodology
- **Dataset:** We utilize the public **Zomato Delivery Time Prediction dataset** (~36,000 rows after cleaning out extreme geospatial outliers and nulls).
- **The "Promised ETA" Baseline:** Because actual, real-world platform ETA routing algorithms are proprietary and not included in public datasets, we derived a synthetic "Promised ETA" using a naive distance/speed formula (factoring in distance, a flat traffic penalty, and restaurant prep time). 
- **The Contribution:** This synthetic baseline serves as a proxy for legacy logic. Establishing this benchmarking methodology to compare against a modern ML baseline is a core contribution of this project.

## Model Approach
We trained a `GradientBoostingRegressor` to predict the actual `Time_taken(min)` based purely on pre-trip environmental and logistical factors:
- `Distance_km` (Derived via Haversine formula from coordinates)
- `Road_traffic_density`
- `Weatherconditions`
- `Type_of_vehicle`
- `multiple_deliveries` (Batched orders)
- `Festival` (High-demand flags)

## Results

The ML model drastically outperforms the naive baseline, successfully predicting the delivery time to within 5 minutes over 70% of the time.

| Metric | Baseline (Naive Formula) | ML Model (Gradient Boosting) | Improvement |
| :--- | :--- | :--- | :--- |
| **MAE** | 11.69 min | **3.84 min** | 67.1% 📉 |
| **RMSE** | 15.08 min | **4.84 min** | 67.9% 📉 |
| **MAPE** | 53.90% | **17.11%** | 68.2% 📉 |
| **Within +/- 5 mins** | 32.35% | **70.90%** | +38.55% 📈 |

## Model Notes / Limitations
- **Regression to the Mean:** Our analysis shows mild regression-to-the-mean at extreme fast or slow deliveries (the test set ranges strictly from 10 to 54 minutes). This is a known characteristic of Gradient Boosting ensembles which optimize for mean squared error. Future work could explore *Quantile Regression* to better calibrate and bound tail-end predictions.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pandas, Scikit-learn
- **Frontend:** React, Vite, Tailwind CSS (v3), Recharts, Axios

---

## How to Run Locally

### 1. Backend Setup
Navigate to the `backend` directory, set up a virtual environment, install the dependencies, and run the FastAPI server.

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
Open a new terminal, navigate to the `frontend` directory, install NPM packages, and start the Vite dev server.

```bash
cd frontend

# Install dependencies
npm install

# Start the dashboard
npm run dev
```
The React dashboard will be accessible at `http://localhost:5173`.
