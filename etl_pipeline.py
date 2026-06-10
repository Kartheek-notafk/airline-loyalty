"""
ETL Pipeline: Extract → Transform → Load
Airline Loyalty Program Analytics Data Warehouse
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# EXTRACT
# ──────────────────────────────────────────────

def extract_raw_data(source_path: str = "dataset") -> dict[str, pd.DataFrame]:
    """
    Extract raw CSVs from the dataset directory.
    """
    logger.info("Starting extraction phase...")
    datasets = {}

    csv_files = {
        "loyalty_history": "Customer Loyalty History.csv",
        "flight_activity": "Customer Flight Activity.csv",
    }

    for key, filename in csv_files.items():
        path = os.path.join(source_path, filename)
        if os.path.exists(path):
            datasets[key] = pd.read_csv(path)
            logger.info("  Loaded %s (%d rows)", filename, len(datasets[key]))
        else:
            raise FileNotFoundError(f"Required dataset file {path} not found.")

    return datasets


# ──────────────────────────────────────────────
# TRANSFORM
# ──────────────────────────────────────────────

def transform(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Clean, enrich, and reshape raw loyalty data into warehouse dimensions and facts."""
    logger.info("Starting transformation phase...")

    history = datasets["loyalty_history"].copy()
    activity = datasets["flight_activity"].copy()

    # 1. Clean and Transform Customer Dimension
    logger.info("Transforming Dimension_Customer...")
    history.rename(columns={
        "Loyalty Number": "customer_id",
        "Country": "country",
        "Province": "province",
        "City": "city",
        "Postal Code": "postal_code",
        "Gender": "gender",
        "Education": "education",
        "Salary": "salary",
        "Marital Status": "marital_status",
        "Loyalty Card": "loyalty_card",
        "CLV": "clv",
        "Enrollment Type": "enrollment_type",
        "Enrollment Year": "enrollment_year",
        "Enrollment Month": "enrollment_month",
        "Cancellation Year": "cancellation_year",
        "Cancellation Month": "cancellation_month"
    }, inplace=True)

    # Impute missing salaries by education level median
    salary_medians = history.groupby("education")["salary"].median()
    logger.info("  Salary medians by education level:")
    for edu, val in salary_medians.items():
        logger.info("    %s: $%.2f", edu, val)
    
    # Fill salary NaNs
    history["salary"] = history.apply(
        lambda row: salary_medians[row["education"]] if pd.isna(row["salary"]) and row["education"] in salary_medians else row["salary"],
        axis=1
    )
    # If any salaries are still null, fill with overall median
    overall_median_salary = history["salary"].median()
    history["salary"] = history["salary"].fillna(overall_median_salary)

    # Standardize loyalty card tier names and check values
    history["loyalty_card"] = history["loyalty_card"].astype(str).str.strip()
    history = history[history["loyalty_card"].isin(["Star", "Nova", "Aurora"])]

    # 2. Clean and Transform Date Dimension
    logger.info("Creating Dimension_Date...")
    # Get all unique year-month combinations from activity and demographics
    dates_df = activity[["Year", "Month"]].drop_duplicates().reset_index(drop=True)
    dates_df = dates_df.sort_values(["Year", "Month"]).reset_index(drop=True)
    
    dates_df["date_id"] = dates_df["Year"] * 100 + dates_df["Month"]
    dates_df["full_date"] = dates_df.apply(lambda row: f"{row['Year']}-{row['Month']:02d}-01", axis=1)
    dates_df["quarter"] = (dates_df["Month"] - 1) // 3 + 1
    
    # Season mapping
    seasons = {12: "Winter", 1: "Winter", 2: "Winter",
               3: "Spring", 4: "Spring", 5: "Spring",
               6: "Summer", 7: "Summer", 8: "Summer",
               9: "Fall", 10: "Fall", 11: "Fall"}
    dates_df["season"] = dates_df["Month"].map(seasons)
    
    # Month Name mapping
    dates_df["month_name"] = dates_df.apply(lambda row: datetime(row["Year"], row["Month"], 1).strftime("%B"), axis=1)
    
    # Holiday flag (December and July are peak holiday travel seasons in Canada)
    dates_df["is_holiday"] = dates_df["Month"].isin([7, 12])

    dim_date = dates_df[["date_id", "full_date", "Month", "Year", "quarter", "season", "is_holiday", "month_name"]].rename(
        columns={"Month": "month", "Year": "year"}
    )

    # 3. Clean and Transform Activity Fact Table
    logger.info("Transforming Fact_Customer_Activity...")
    activity.rename(columns={
        "Loyalty Number": "customer_id",
        "Year": "year",
        "Month": "month",
        "Total Flights": "total_flights",
        "Distance": "distance",
        "Points Accumulated": "points_accumulated",
        "Points Redeemed": "points_redeemed",
        "Dollar Cost Points Redeemed": "dollar_cost_points_redeemed"
    }, inplace=True)

    # Map year and month to date_id
    activity["date_id"] = activity["year"] * 100 + activity["month"]

    # Filter activity rows to ensure they reference existing customers
    existing_customers = set(history["customer_id"])
    activity_len_before = len(activity)
    activity = activity[activity["customer_id"].isin(existing_customers)]
    logger.info("  Filtered fact table: kept %d rows out of %d (dropped %d invalid customers)", 
                len(activity), activity_len_before, activity_len_before - len(activity))

    # Keep only target DWH fact columns
    fact_activity = activity[[
        "customer_id", "date_id", "total_flights", "distance", 
        "points_accumulated", "points_redeemed", "dollar_cost_points_redeemed"
    ]]

    logger.info("  Transformation complete: %d customers, %d dates, %d activities", 
                len(history), len(dim_date), len(fact_activity))

    return {
        "dim_customer": history,
        "dim_date": dim_date,
        "fact_activity": fact_activity,
    }


# ──────────────────────────────────────────────
# LOAD
# ──────────────────────────────────────────────

def load(transformed: dict[str, pd.DataFrame], output_dir: str = "data/processed") -> None:
    """Write transformed tables to the processed data directory."""
    logger.info("Starting load phase → %s", output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for name, df in transformed.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        logger.info("  Saved %s (%d rows, %d cols)", path, len(df), len(df.columns))

    logger.info("Load phase complete.")


# ──────────────────────────────────────────────
# ORCHESTRATOR
# ──────────────────────────────────────────────

def run_pipeline(source_path: str = "dataset", output_dir: str = "data/processed") -> None:
    logger.info("=" * 55)
    logger.info("  Airline Loyalty ETL Pipeline  —  %s", datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info("=" * 55)

    try:
        raw = extract_raw_data(source_path)
        transformed = transform(raw)
        load(transformed, output_dir)
        logger.info("Pipeline finished successfully.")
    except Exception as e:
        logger.error("Pipeline failed: %s", str(e), exc_info=True)
        raise e


if __name__ == "__main__":
    run_pipeline()