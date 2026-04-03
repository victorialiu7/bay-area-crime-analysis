# Prepares data to be optimal for Tableau 
# Created a combined dataset for comparison analysis 

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/clean")
OUTPUT_DIR = Path("data/tableau")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def prepare_tableau_data():
    """Prepare datasets for Tableau with optimal formatting."""
    
    # Load cleaned data
    print("Loading cleaned datasets...")
    sf_df = pd.read_csv(DATA_DIR / "sf_clean.csv")
    oak_df = pd.read_csv(DATA_DIR / "oak_clean.csv")
    
    # Convert datetime columns
    sf_df["datetime"] = pd.to_datetime(sf_df["datetime"])
    sf_df["date"] = pd.to_datetime(sf_df["date"])
    oak_df["datetime"] = pd.to_datetime(oak_df["datetime"])
    oak_df["date"] = pd.to_datetime(oak_df["date"])
    
    # Add derived fields useful for Tableau
    # Hour of day
    sf_df["hour"] = sf_df["datetime"].dt.hour
    oak_df["hour"] = oak_df["datetime"].dt.hour
    
    # Day of week
    sf_df["day_of_week"] = sf_df["datetime"].dt.day_name()
    oak_df["day_of_week"] = oak_df["datetime"].dt.day_name()
    
    # Day of week number (0=Monday, 6=Sunday)
    sf_df["day_of_week_num"] = sf_df["datetime"].dt.dayofweek
    oak_df["day_of_week_num"] = oak_df["datetime"].dt.dayofweek
    
    # Month name
    sf_df["month_name"] = sf_df["datetime"].dt.month_name()
    oak_df["month_name"] = oak_df["datetime"].dt.month_name()
    
    # Quarter
    sf_df["quarter"] = sf_df["datetime"].dt.quarter
    oak_df["quarter"] = oak_df["datetime"].dt.quarter
    
    # Year-Month for easier filtering
    sf_df["year_month"] = sf_df["datetime"].dt.to_period("M").astype(str)
    oak_df["year_month"] = oak_df["datetime"].dt.to_period("M").astype(str)
    
    # Standardize column names for combined dataset
    # SF has: incident_id, subcategory, district
    # Oakland has: case_number, description, beat
    
    # Rename for consistency in combined dataset
    sf_combined = sf_df.copy()
    sf_combined = sf_combined.rename(columns={
        "incident_id": "record_id",
        "subcategory": "detail",
        "district": "area"
    })
    sf_combined["area_type"] = "District"
    sf_combined["detail_type"] = "Subcategory"
    
    oak_combined = oak_df.copy()
    oak_combined = oak_combined.rename(columns={
        "case_number": "record_id",
        "description": "detail",
        "beat": "area"
    })
    oak_combined["area_type"] = "Beat"
    oak_combined["detail_type"] = "Description"
    
    # Select common columns for combined dataset
    common_cols = [
        "city", "period_code", "period_label",
        "record_id", "datetime", "date", "year", "month", "year_month",
        "month_name", "quarter", "hour", "day_of_week", "day_of_week_num",
        "category", "detail", "detail_type",
        "area", "area_type",
        "latitude", "longitude"
    ]
    
    # Create combined dataset
    combined_df = pd.concat([
        sf_combined[common_cols],
        oak_combined[common_cols]
    ], ignore_index=True)
    
    # Save individual files (optimized for Tableau)
    # print("\nSaving Tableau-ready files...")
    # sf_df.to_csv(OUTPUT_DIR / "sf_tableau.csv", index=False)
    # print(f"Saved sf_tableau.csv ({len(sf_df):,} rows)")
    
    # oak_df.to_csv(OUTPUT_DIR / "oak_tableau.csv", index=False)
    # print(f"Saved oak_tableau.csv ({len(oak_df):,} rows)")
    
    # Save combined file
    combined_df.to_csv(OUTPUT_DIR / "combined_tableau.csv", index=False)
    print(f"Saved combined_tableau.csv ({len(combined_df):,} rows)")
    
    # Create summary statistics file for reference
    summary = {
        "San Francisco": {
            "total_records": len(sf_df),
            "date_range": f"{sf_df['date'].min()} to {sf_df['date'].max()}",
            "unique_categories": sf_df["category"].nunique(),
            "unique_districts": sf_df["district"].nunique() if "district" in sf_df.columns else 0,
        },
        "Oakland": {
            "total_records": len(oak_df),
            "date_range": f"{oak_df['date'].min()} to {oak_df['date'].max()}",
            "unique_categories": oak_df["category"].nunique(),
            "unique_beats": oak_df["beat"].nunique() if "beat" in oak_df.columns else 0,
        },
        "Combined": {
            "total_records": len(combined_df),
            "unique_cities": combined_df["city"].nunique(),
            "unique_categories": combined_df["category"].nunique(),
        }
    }
    
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    for dataset, stats in summary.items():
        print(f"\n{dataset}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("Files saved to:", OUTPUT_DIR)

if __name__ == "__main__":
    prepare_tableau_data()

