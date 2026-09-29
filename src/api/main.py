from pathlib import Path
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Customer Behavior Prediction API",
    description="API for customer analytics, lifetime value, and churn risk prediction.",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "churn_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "customer_features.csv"

# Load model and precomputed features on startup
model_data = None
features_df = None

@app.on_event("startup")
def load_artifacts():
    global model_data, features_df
    if MODEL_PATH.exists():
        model_data = joblib.load(MODEL_PATH)
        print("Loaded ML model successfully.")
    else:
        print("Warning: Model artifact not found!")
        
    if FEATURES_PATH.exists():
        features_df = pd.read_csv(FEATURES_PATH)
        print("Loaded customer features successfully.")
    else:
        print("Warning: Customer features dataset not found!")

class CustomerPredictionInput(BaseModel):
    recency_days: float
    frequency: int
    monetary: float
    avg_basket_size: float
    avg_item_price: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Customer Behavior Prediction API!"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_data is not None,
        "features_loaded": features_df is not None,
        "total_customers": len(features_df) if features_df is not None else 0
    }

@app.get("/api/summary")
def get_summary():
    if features_df is None:
        raise HTTPException(status_code=500, detail="Customer features not loaded.")
    
    total_customers = int(len(features_df))
    total_revenue = float(features_df["monetary"].sum())
    avg_order_value = float(features_df["monetary"].mean())
    churn_rate = float(features_df["churn"].mean())
    
    return {
        "total_customers": total_customers,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(avg_order_value, 2),
        "churn_rate": round(churn_rate, 4)
    }

@app.get("/api/customers")
def get_customers(limit: int = 50, offset: int = 0, search: str = None):
    if features_df is None:
        raise HTTPException(status_code=500, detail="Customer features not loaded.")
    
    df = features_df.copy()
    if search:
        df = df[df["Customer_ID"].astype(str).str.contains(search, case=False)]
        
    paginated = df.iloc[offset:offset + limit]
    return {
        "total": len(df),
        "limit": limit,
        "offset": offset,
        "customers": paginated.to_dict(orient="records")
    }

@app.get("/api/customers/{customer_id}")
def get_customer_detail(customer_id: str):
    if features_df is None:
        raise HTTPException(status_code=500, detail="Customer features not loaded.")
        
    customer = features_df[features_df["Customer_ID"].astype(str) == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer not found.")
        
    return customer.to_dict(orient="records")[0]

@app.post("/api/predict")
def predict_churn(input_data: CustomerPredictionInput):
    if model_data is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
        
    model = model_data["model"]
    feature_cols = model_data["feature_cols"]
    
    input_df = pd.DataFrame([{
        "recency_days": input_data.recency_days,
        "frequency": input_data.frequency,
        "monetary": input_data.monetary,
        "avg_basket_size": input_data.avg_basket_size,
        "avg_item_price": input_data.avg_item_price
    }][feature_cols])
    
    pred = int(model.predict(input_df)[0])
    prob = float(model.predict_proba(input_df)[0][1]) if hasattr(model, "predict_proba") else float(pred)
    
    risk_level = "High" if prob > 0.7 else ("Medium" if prob > 0.4 else "Low")
    
    return {
        "churn_prediction": pred,
        "churn_probability": round(prob, 4),
        "risk_level": risk_level
    }