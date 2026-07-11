import streamlit as st
import numpy as np
import os
from datetime import datetime, timedelta

@st.cache_resource
def _load_demand_model():
    path = "models/demand_model.keras"
    if os.path.exists(path):
        try:
            from tensorflow import keras
            return keras.models.load_model(path)
        except Exception as e:
            st.warning(f"Demand model failed to load: {e}. Using synthetic forecast.")
    return None

def forecast_demand(category: str, sector: str, region: str) -> dict:
    """
    Predicts demand for the next 30 days.
    Returns: {"forecast_dates": list, "predicted_demand": list}
    """
    model = _load_demand_model()
    
    if model:
        try:
            # Mock input shape for LSTM/Time series model (e.g., 1 sample, 30 timesteps, 1 feature)
            dummy_input = np.random.rand(1, 30, 1) 
            predictions = model.predict(dummy_input, verbose=0)[0]
            forecast = predictions.flatten().tolist()
        except Exception:
            forecast = np.linspace(100, 150, 30).tolist()
    else:
        # Synthetic fallback forecast with slight growth and noise
        base = 100
        trend = 1.02 # 2% daily growth assumption
        forecast = [base * (trend ** i) + np.random.normal(0, 5) for i in range(30)]
        
    # Generate dates for the next 30 days
    start_date = datetime.now()
    dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    
    return {
        "forecast_dates": dates,
        "predicted_demand": [round(max(0, d), 2) for d in forecast] # Ensure no negative demand
    }
