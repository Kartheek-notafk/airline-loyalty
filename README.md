# Airline Loyalty Program Analytics

## Project Overview

This repository is a small airline data warehouse and analytics project built to explore customer loyalty behavior, flight activity, and demand forecasting for an airline loyalty program.

The project includes:
- an ETL pipeline that transforms raw loyalty and flight activity CSV files into warehouse-ready dimension and fact tables
- a Streamlit analytics dashboard for interactive exploration of customer loyalty, flight metrics, and loyalty program performance
- a machine learning modeling script for CLV prediction and flight demand forecasting
- SQL schema and reporting artifacts to support a star-schema warehouse design

## What this project stands for

This project demonstrates how to build a practical airline analytics solution from raw customer loyalty data through:
- data extraction, transformation, and loading (ETL)
- dimension and fact table construction for a data warehouse
- exploratory and dashboard reporting using modern visual analytics
- machine learning for customer lifetime value and airline demand forecasting
- a polished user experience with Streamlit metrics, filters, and charting

## Repository Structure

- `app.py` - Streamlit application for airline loyalty and demographics analytics
- `etl_pipeline.py` - ETL pipeline that loads raw CSVs from `dataset/`, cleans and transforms them, and writes processed output to `data/processed/`
- `demand_forecasting.py` - ML modeling and forecasting script for CLV prediction and flight demand
- `requirements.txt` - Python package dependencies required to run the app and scripts
- `dataset/` - raw source data files
- `data/processed/` - generated processed data files used by the dashboard and models
- `*.sql` - SQL files for warehouse schema, facts, dimensions, views, and analysis queries

## Data Sources

Raw source files are stored in `dataset/`:
- `Customer Flight Activity.csv`
- `Customer Loyalty History.csv`

Processed warehouse tables are written to `data/processed/`:
- `dim_customer.csv` - customer demographic and loyalty profile dimension
- `dim_date.csv` - date dimension with month/year/season and holiday flags
- `fact_activity.csv` - flight activity fact table with flights, distance, points, and costs

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build the processed data files from raw source data:
```bash
python etl_pipeline.py
```

3. Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

4. Optionally run the ML forecasting and CLV training script:
```bash
python demand_forecasting.py
```

## What Each Script Does

### `etl_pipeline.py`
- reads raw CSVs from `dataset/`
- cleans and standardizes customer loyalty demographic fields
- generates a date dimension with month, quarter, season, and holiday indicators
- creates a fact table for customer flight activity
- writes processed tables to `data/processed/`

### `app.py`
- loads preprocessed warehouse tables
- provides filters for year, loyalty tier, and province
- displays KPI cards, charts, and analytics for airline loyalty performance
- uses Streamlit with Plotly visualizations for a premium dashboard experience

### `demand_forecasting.py`
- loads processed warehouse tables
- trains CLV prediction models using customer demographic features
- trains demand forecasting models on monthly flight activity trends
- reports model metrics for MAE, RMSE, and R²

## Dependencies

Key Python packages:
- `streamlit`
- `pandas`
- `numpy`
- `plotly`
- `scikit-learn`
- `xgboost` (optional, if installed)

## Notes

- Be sure to run `etl_pipeline.py` first to generate the `data/processed/` files required by `app.py` and `demand_forecasting.py`.
- The SQL scripts illustrate the warehouse schema and support analytical queries for customer loyalty and flight activity.

## License

This project is provided as a demonstration of airline loyalty analytics and warehouse design. Feel free to adapt the structure and analyses for your own airline or loyalty program use cases.
