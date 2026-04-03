import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/clean")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# period_code: 0=pre, 1=covid, 2=post
SF_FILES = [
    (RAW_DIR / "sf_sfpd_incidents_raw_pre_covid.csv", 0, "pre"),
    (RAW_DIR / "sf_sfpd_incidents_raw_covid.csv", 1, "covid"),
    (RAW_DIR / "sf_sfpd_incidents_raw_post_covid.csv", 2, "post"),
]

def clean_sf_one(path: Path, period_code: int, period_label: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Rename to clean, consistent names
    df = df.rename(columns={
        "incident_id": "incident_id",
        "incident_datetime": "datetime",
        "incident_category": "category",
        "incident_subcategory": "subcategory",
        "police_district": "district",
        "latitude": "latitude",
        "longitude": "longitude",
    })

    # Parse datetime + coords
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Drop unusable rows (required for maps/time series)
    df = df.dropna(subset=["datetime", "latitude", "longitude"])

    # Sanity bounds (helps remove junk rows)
    df = df[df["latitude"].between(37.6, 37.95) & df["longitude"].between(-122.55, -122.35)]

    # Add period labels
    df["period_code"] = period_code
    df["period_label"] = period_label
    df["city"] = "San Francisco"

    # Derived fields for analysis/Tableau
    df["date"] = df["datetime"].dt.date
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.to_period("M").astype(str)

    # Light text cleanup
    for col in ["category", "subcategory", "district"]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA})

    # Keep final columns (Tableau-friendly)
    cols = [
        "city", "period_code", "period_label",
        "incident_id", "datetime", "date", "year", "month",
        "category", "subcategory", "district",
        "latitude", "longitude",
    ]
    return df[cols].drop_duplicates(subset=["incident_id"])

def main():
    frames = []
    for path, code, label in SF_FILES:
        if not path.exists():
            raise FileNotFoundError(f"Missing SF raw file: {path}")
        frames.append(clean_sf_one(path, code, label))

    out = pd.concat(frames, ignore_index=True)
    out_path = OUT_DIR / "sf_clean.csv"
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path} shape={out.shape}")

if __name__ == "__main__":
    main()
