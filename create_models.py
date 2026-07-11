import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
import tensorflow as tf
from tensorflow import keras

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

print("🤖 Creating AI models for EthioChain...")

# 1. Fraud Detection Model (XGBoost/RandomForest)
print("1/4: Creating fraud detection model...")
X_fraud = np.random.rand(1000, 2)  # amount, payment_method_encoded
y_fraud = np.random.randint(0, 2, 1000)
fraud_model = RandomForestClassifier(n_estimators=100, random_state=42)
fraud_model.fit(X_fraud, y_fraud)
with open("models/fraud_model.pkl", "wb") as f:
    pickle.dump(fraud_model, f)
print("✅ Saved models/fraud_model.pkl")

# 2. Supplier/Merchant Matching Model (K-Means)
print("2/4: Creating matching model...")
X_match = np.random.rand(500, 2)  # sector_encoded, city_encoded
matching_model = KMeans(n_clusters=10, random_state=42, n_init=10)
matching_model.fit(X_match)
with open("models/matching_model.pkl", "wb") as f:
    pickle.dump(matching_model, f)
print("✅ Saved models/matching_model.pkl")

# 3. Price Recommendation Model (RandomForest Regressor)
print("3/4: Creating price recommendation model...")
X_price = np.random.rand(800, 3)  # category_encoded, quantity, city_encoded
y_price = np.random.rand(800) * 10000  # price in ETB
price_model = RandomForestRegressor(n_estimators=100, random_state=42)
price_model.fit(X_price, y_price)
with open("models/price_model.pkl", "wb") as f:
    pickle.dump(price_model, f)
print("✅ Saved models/price_model.pkl")

# 4. Demand Forecasting Model (LSTM)
print("4/4: Creating demand forecasting model...")
# Simple LSTM for time series
model = keras.Sequential([
    keras.layers.LSTM(50, activation='relu', input_shape=(30, 1)),
    keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# Train on dummy data
X_demand = np.random.rand(100, 30, 1)
y_demand = np.random.rand(100, 1)
model.fit(X_demand, y_demand, epochs=5, verbose=0)
model.save("models/demand_model.keras")
print("✅ Saved models/demand_model.keras")

# 5. Product Recommendation Model (RandomForest for collaborative filtering mock)
print("5/5: Creating recommendation model...")
X_rec = np.random.rand(600, 1)  # num_past_purchases
y_rec = np.random.rand(600) * 100  # recommendation scores
rec_model = RandomForestRegressor(n_estimators=50, random_state=42)
rec_model.fit(X_rec, y_rec)
with open("models/recommendation_model.pkl", "wb") as f:
    pickle.dump(rec_model, f)
print("✅ Saved models/recommendation_model.pkl")

print("\n🎉 All models created successfully!")
print("You can now deploy the application.")
