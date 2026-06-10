"""
ML Modeling and Demand Forecasting
Airline Loyalty Program Analytics Data Warehouse
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import warnings
import logging
import os
import json

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    logging.warning("XGBoost not installed – skipping XGB model.")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# DATA PREPARATION
# ──────────────────────────────────────────────

def load_processed_data(data_dir: str = "data/processed") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the processed loyalty tables."""
    cust_path = os.path.join(data_dir, "dim_customer.csv")
    act_path = os.path.join(data_dir, "fact_activity.csv")
    date_path = os.path.join(data_dir, "dim_date.csv")

    if os.path.exists(cust_path) and os.path.exists(act_path) and os.path.exists(date_path):
        customers = pd.read_csv(cust_path)
        activity = pd.read_csv(act_path)
        dates = pd.read_csv(date_path)
        
        # Merge activities with date info for time series aggregates
        df_merged = activity.merge(customers, on="customer_id", how="inner")
        df_merged = df_merged.merge(dates, on="date_id", how="inner")
        
        logger.info("Loaded %d activity records merged with customer demographics.", len(df_merged))
        return customers, df_merged

    raise FileNotFoundError("Processed datasets not found in data/processed directory. Run ETL pipeline first.")


# ──────────────────────────────────────────────
# MODEL 1: CUSTOMER LIFETIME VALUE (CLV) PREDICTION
# ──────────────────────────────────────────────

CLV_FEATURE_COLS = ["gender", "education", "marital_status", "loyalty_card", "salary", "enrollment_type"]

def train_clv_models(customers: pd.DataFrame) -> dict:
    """Train and evaluate models to predict CLV from demographics."""
    logger.info("Training Customer Lifetime Value (CLV) prediction models...")
    
    # Preprocessing
    df = customers.copy()
    
    # Label encode categorical columns
    le_dict = {}
    categorical_cols = ["gender", "education", "marital_status", "loyalty_card", "enrollment_type"]
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        le_dict[col] = le
        
    df = df.dropna(subset=CLV_FEATURE_COLS + ["clv"])

    X = df[CLV_FEATURE_COLS].values
    y = df["clv"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model",  LinearRegression()),
        ]),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        ),
    }
    
    if XGB_AVAILABLE:
        models["XGBoost"] = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, verbosity=0
        )

    results = {}
    trained_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[name] = {
            "MAE":  round(mean_absolute_error(y_test, y_pred),   2),
            "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "R2":   round(r2_score(y_test, y_pred), 4),
        }
        trained_models[name] = model
        logger.info("  %-22s  MAE=%.0f  RMSE=%.0f  R²=%.4f",
                    name, results[name]["MAE"], results[name]["RMSE"], results[name]["R2"])

    return results, trained_models, X_test, y_test


# ──────────────────────────────────────────────
# MODEL 2: MONTHLY FLIGHT DEMAND FORECASTING (lags)
# ──────────────────────────────────────────────

def train_demand_models(df_merged: pd.DataFrame) -> dict:
    """Forecast total monthly flights booked using historical lags."""
    logger.info("Training monthly flights forecasting models...")

    # Group activities by year and month to get overall monthly flight demand
    monthly = (
        df_merged.groupby(["year", "month"])
        .agg(
            total_flights=("total_flights", "sum"),
            avg_distance=("distance", "mean"),
            points_acc=("points_accumulated", "sum")
        )
        .reset_index()
    )
    
    # Sort chronologically to create correct lags
    monthly = monthly.sort_values(["year", "month"]).reset_index(drop=True)
    
    # Generate lag features
    monthly["lag1"] = monthly["total_flights"].shift(1)
    monthly["lag2"] = monthly["total_flights"].shift(2)
    
    # Drop rows with NaN lag values
    monthly = monthly.dropna()

    if len(monthly) < 5:
        logger.warning("Not enough chronological months to perform lag forecasting. Skipping Demand Models.")
        return {}

    feat_cols = ["year", "month", "avg_distance", "points_acc", "lag1", "lag2"]
    X = monthly[feat_cols].values
    y = monthly["total_flights"].values

    # Given small time series size (24 months total in dataset, minus 2 lags = 22 rows), 
    # we'll do a simple train/test split.
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    y_pred = rf.predict(X_te)

    result = {
        "Random Forest": {
            "MAE":  round(mean_absolute_error(y_te, y_pred), 2),
            "RMSE": round(np.sqrt(mean_squared_error(y_te, y_pred)), 2),
            "R2":   round(r2_score(y_te, y_pred), 4),
        }
    }
    logger.info("  Demand RF  MAE=%.0f  RMSE=%.0f  R²=%.4f",
                result["Random Forest"]["MAE"],
                result["Random Forest"]["RMSE"],
                result["Random Forest"]["R2"])
    
    return result


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    try:
        customers, df_merged = load_processed_data()
        
        # Train CLV Models
        clv_results, models, X_test, y_test = train_clv_models(customers)
        
        # Train Demand Forecast Model
        dem_results = train_demand_models(df_merged)

        print("\n===  CLV Model Results  ===")
        for name, m in clv_results.items():
            print(f"  {name:<22}  MAE={m['MAE']:>8,.0f}  R²={m['R2']:.4f}")

        if dem_results:
            print("\n===  Flights Forecasting Model Results  ===")
            for name, m in dem_results.items():
                print(f"  {name:<22}  MAE={m['MAE']:>8,.0f}  R²={m['R2']:.4f}")
                
    except Exception as e:
        logger.error("ML training script failed: %s", str(e), exc_info=True)