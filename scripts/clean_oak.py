# scripts/clean_oak.py
import ast
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/clean")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# period_code: 0=pre, 1=covid, 2=post
OAK_FILES = [
    (RAW_DIR / "oakland_crimewatch_raw_pre_covid.csv", 0, "pre"),
    (RAW_DIR / "oakland_crimewatch_raw_covid.csv", 1, "covid"),
    (RAW_DIR / "oakland_crimewatch_raw_post_covid.csv", 2, "post"),
]

def parse_location_to_lat_lon(x):
    """
    x is a string like: "{'type': 'Point', 'coordinates': [-122.27, 37.80]}"
    Returns (lat, lon) or (None, None) if parsing fails.
    """
    if pd.isna(x):
        return (None, None)

    obj = x
    if isinstance(x, str):
        x = x.strip()
        if not x:
            return (None, None)
        try:
            obj = ast.literal_eval(x)  # safe parsing of string dict
        except Exception:
            return (None, None)

    if isinstance(obj, dict) and obj.get("type") == "Point":
        coords = obj.get("coordinates")
        if isinstance(coords, list) and len(coords) == 2:
            lon, lat = coords[0], coords[1]  # GeoJSON order is [lon, lat]
            return (lat, lon)

    return (None, None)

def clean_oak_one(path: Path, period_code: int, period_label: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Normalize column names to a clean schema
    df = df.rename(columns={
        "casenumber": "case_number",
        "datetime": "datetime",
        "crimetype": "category",
        "description": "description",
        "policebeat": "beat",
        "address": "address",
        "city": "city",
        "location": "location",
    })

    # Parse datetime
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    # Extract lat/lon from GeoJSON point
    latlon = df["location"].apply(parse_location_to_lat_lon)
    df["latitude"] = latlon.apply(lambda t: t[0])
    df["longitude"] = latlon.apply(lambda t: t[1])

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Drop unusable rows for maps/time series
    df = df.dropna(subset=["datetime", "latitude", "longitude"])

    # Add period labels
    df["period_code"] = period_code
    df["period_label"] = period_label

    # Helpful derived fields
    df["date"] = df["datetime"].dt.date
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.to_period("M").astype(str)

    # Light text cleanup
    for col in ["category", "description", "beat", "address", "city"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"": pd.NA})

    # Keep final columns (Tableau-friendly)
    cols = [
        "city", "period_code", "period_label",
        "case_number", "datetime", "date", "year", "month",
        "category", "description", "beat", "address",
        "latitude", "longitude",
    ]
    return df[cols].drop_duplicates(subset=["case_number", "datetime"])

def main():
    frames = []
    for path, code, label in OAK_FILES:
        if not path.exists():
            raise FileNotFoundError(f"Missing Oakland raw file: {path}")
        frames.append(clean_oak_one(path, code, label))

    out = pd.concat(frames, ignore_index=True)
    out_path = OUT_DIR / "oak_clean.csv"
    out.to_csv(out_path, index=False)
    print(f"Saved {out_path} shape={out.shape}")

if __name__ == "__main__":
    main()
