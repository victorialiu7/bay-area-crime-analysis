import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def socrata_fetch_all(
    domain: str,
    dataset_id: str,
    where: str,
    select: str,
    chunk_size: int = 50000,
    max_rows: int = 800000,
    sleep_s: float = 0.2,
):
    """
    Use Socrata SODA to fetch data.
    Returns a pandas DataFrame with raw (messy) records.
    """
    base = f"https://{domain}/resource/{dataset_id}.json"
    headers = {"User-Agent": "bay-area-sf-oak-scraper/1.0"}

    token = os.getenv("SOCRATA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token

    all_rows = []
    offset = 0

    while True:
        params = {
            "$select": select,
            "$where": where,
            "$limit": chunk_size,
            "$offset": offset,
        }
        r = requests.get(base, params=params, headers=headers, timeout=60)

        if r.status_code != 200:
            print("STATUS:", r.status_code)
            print("URL:", r.url)
            print("BODY:", r.text[:2000])

        r.raise_for_status()
        batch = r.json()

        if not batch:
            break

        all_rows.extend(batch)
        offset += chunk_size
        print(f"[{domain}/{dataset_id}] fetched {len(all_rows):,} rows...")

        if len(all_rows) >= max_rows:
            print(f"Reached max_rows={max_rows}. Stopping early.")
            break

        time.sleep(sleep_s)

    return pd.DataFrame(all_rows)

def scrape_sf(start_iso: str, end_iso_exclusive: str, label: str):
    """
    SF SFPD Incident Reports (2018–present): dataset wg3w-h783
    """
    domain = "data.sfgov.org"
    dataset_id = "wg3w-h783"

    select = ",".join([
        "incident_id",
        "incident_datetime",
        "incident_category",
        "incident_subcategory",
        "police_district",
        "latitude",
        "longitude"
    ])

    where = f"incident_datetime >= '{start_iso}' AND incident_datetime < '{end_iso_exclusive}'"
    df = socrata_fetch_all(domain, dataset_id, where, select)

    os.makedirs("data/raw", exist_ok=True)
    outpath = f"data/raw/sf_sfpd_incidents_raw_{label}.csv"
    df.to_csv(outpath, index=False)
    print(f"Saved {outpath} {df.shape}")

def scrape_oakland(start_date: str, end_date_exclusive: str, label: str):
    """
    Oakland CrimeWatch: ppgh-7dqv
    """
    domain = "data.oaklandca.gov"
    dataset_id = "ppgh-7dqv"

    select = ",".join([
        "casenumber",
        "datetime",
        "crimetype",
        "description",
        "policebeat",
        "address",
        "city",
        "state",
        "location"
    ])

    where = f"datetime >= '{start_date}' AND datetime < '{end_date_exclusive}'"
    df = socrata_fetch_all(domain, dataset_id, where, select, max_rows=800000)

    os.makedirs("data/raw", exist_ok=True)
    outpath = f"data/raw/oakland_crimewatch_raw_{label}.csv"
    df.to_csv(outpath, index=False)
    print(f"Saved {outpath} {df.shape}")

def main():
    # Analysis windows:
    # Pre-COVID: 2018-01-01 to 2020-01-01 (covers 2018-2019)
    # COVID:     2020-01-01 to 2022-01-01 (covers 2020-2021)
    # Post:      2022-01-01 to 2024-01-01 (covers 2022-2023)
    windows = [
        ("pre_covid",  "2018-01-01T00:00:00.000", "2020-01-01T00:00:00.000", "2018-01-01", "2020-01-01"),
        ("covid",      "2020-01-01T00:00:00.000", "2022-01-01T00:00:00.000", "2020-01-01", "2022-01-01"),
        ("post_covid", "2022-01-01T00:00:00.000", "2024-01-01T00:00:00.000", "2022-01-01", "2024-01-01"),
    ]

    for label, sf_start, sf_end, oak_start, oak_end in windows:
        print("\n" + "=" * 60)
        print(f"SCRAPING WINDOW: {label}")
        print("=" * 60)

        scrape_sf(sf_start, sf_end, label)
        scrape_oakland(oak_start, oak_end, label)

if __name__ == "__main__":
    main()
