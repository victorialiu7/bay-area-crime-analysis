import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

DATA_DIR = Path("data/clean")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load both SF and Oakland data."""
    sf_df = pd.read_csv(DATA_DIR / "sf_clean.csv")
    oak_df = pd.read_csv(DATA_DIR / "oak_clean.csv")
    
    sf_df["datetime"] = pd.to_datetime(sf_df["datetime"])
    sf_df["date"] = pd.to_datetime(sf_df["date"])
    oak_df["datetime"] = pd.to_datetime(oak_df["datetime"])
    oak_df["date"] = pd.to_datetime(oak_df["date"])
    
    return sf_df, oak_df

def city_comparison(sf_df, oak_df):
    """Compare overall statistics between cities."""
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)
    
    # Overall statistics
    print("\nOverall Statistics:")
    print(f"San Francisco: {len(sf_df):,} incidents")
    print(f"Oakland: {len(oak_df):,} incidents")
    print(f"Total: {len(sf_df) + len(oak_df):,} incidents")
    
    # Date ranges
    print(f"\nDate Ranges:")
    print(f"San Francisco: {sf_df['date'].min()} to {sf_df['date'].max()}")
    print(f"Oakland: {oak_df['date'].min()} to {oak_df['date'].max()}")
    
    # Period breakdown
    print("\nPeriod Breakdown:")
    print("\nSan Francisco:")
    sf_periods = sf_df.groupby("period_label").size()
    for period, count in sf_periods.items():
        print(f"  {period}: {count:,}")

    print("\nOakland:")
    oak_periods = oak_df.groupby("period_label").size()
    for period, count in oak_periods.items():
        print(f"  {period}: {count:,}")
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Total incidents by city
    ax1 = axes[0, 0]
    city_counts = pd.Series({
        "San Francisco": len(sf_df),
        "Oakland": len(oak_df)
    })
    bars = ax1.bar(city_counts.index, city_counts.values, color=["blue", "red"])
    ax1.bar_label(bars, fmt='{:,.0f}', padding=3)
    ax1.set_title("Total Incidents by City", fontweight="bold")
    ax1.set_ylabel("Number of Incidents")
    ax1.grid(True, alpha=0.3, axis="y")
    
    # 2. Incidents by period (both cities)
    ax2 = axes[0, 1]
    sf_period = sf_df.groupby("period_label").size()
    oak_period = oak_df.groupby("period_label").size()
    period_df = pd.DataFrame({
        "San Francisco": sf_period,
        "Oakland": oak_period
    })
    period_df.plot(kind="bar", ax=ax2, color=["blue", "red"])
    for container in ax2.containers:
        ax2.bar_label(container, fmt='{:,.0f}', padding=3)
    ax2.set_title("Incidents by Period (Both Cities)", fontweight="bold")
    ax2.set_xlabel("Period")
    ax2.set_ylabel("Number of Incidents")
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
    
    # 3. Monthly trends comparison
    ax3 = axes[1, 0]
    sf_monthly = sf_df.groupby("month").size().reset_index(name="count")
    sf_monthly["month_dt"] = pd.to_datetime(sf_monthly["month"])
    sf_monthly = sf_monthly.sort_values("month_dt")
    
    oak_monthly = oak_df.groupby("month").size().reset_index(name="count")
    oak_monthly["month_dt"] = pd.to_datetime(oak_monthly["month"])
    oak_monthly = oak_monthly.sort_values("month_dt")
    
    ax3.plot(sf_monthly["month_dt"], sf_monthly["count"], 
                marker="o", label="San Francisco", color="blue")
    ax3.plot(oak_monthly["month_dt"], oak_monthly["count"], 
            marker="o", label="Oakland", color="red")
    ax3.set_title("Monthly Crime Trends Comparison", fontweight="bold")
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Number of Incidents")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Yearly comparison
    ax4 = axes[1, 1]
    sf_yearly = sf_df.groupby("year").size()
    oak_yearly = oak_df.groupby("year").size()
    yearly_df = pd.DataFrame({
        "San Francisco": sf_yearly,
        "Oakland": oak_yearly
    })
    yearly_df.plot(kind="bar", ax=ax4, color=["blue", "red"])
    for container in ax4.containers:
        ax4.bar_label(container, fmt='{:,.0f}', padding=3)
    ax4.set_title("Yearly Crime Counts Comparison", fontweight="bold")
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Number of Incidents")
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis="y")
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "combined_city_comparison.png", dpi=300, bbox_inches="tight")
    print(f"\nSaved city comparison plot: {OUTPUT_DIR / 'combined_city_comparison.png'}")
    plt.close()

def period_impact_comparison(sf_df, oak_df):
    """Compare how COVID impacted each city."""
    print("\n" + "="*60)
    print("PERIOD IMPACT COMPARISON")
    print("="*60)
    
    # Calculate percentage changes
    sf_pre = len(sf_df[sf_df["period_label"] == "pre"])
    sf_covid = len(sf_df[sf_df["period_label"] == "covid"])
    sf_post = len(sf_df[sf_df["period_label"] == "post"])
    
    oak_pre = len(oak_df[oak_df["period_label"] == "pre"])
    oak_covid = len(oak_df[oak_df["period_label"] == "covid"])
    oak_post = len(oak_df[oak_df["period_label"] == "post"])
    
    sf_covid_change = ((sf_covid - sf_pre) / sf_pre) * 100
    sf_post_change = ((sf_post - sf_pre) / sf_pre) * 100
    
    oak_covid_change = ((oak_covid - oak_pre) / oak_pre) * 100
    oak_post_change = ((oak_post - oak_pre) / oak_pre) * 100
    
    print("\nPercentage Change from Pre-COVID:")
    print(f"\nSan Francisco:")
    print(f"  COVID period: {sf_covid_change:+.2f}%")
    print(f"  Post-COVID period: {sf_post_change:+.2f}%")
    
    print(f"\nOakland:")
    print(f"  COVID period: {oak_covid_change:+.2f}%")
    print(f"  Post-COVID period: {oak_post_change:+.2f}%")
    
    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. COVID impact
    ax1 = axes[0]
    covid_changes = pd.Series({
        "San Francisco": sf_covid_change,
        "Oakland": oak_covid_change
    })
    colors = ["red" if x < 0 else "green" for x in covid_changes.values]
    bars = ax1.bar(covid_changes.index, covid_changes.values, color=colors)
    ax1.axhline(y=0, color="black", linestyle="-")
    ax1.set_title("COVID Period Change from Pre-COVID", fontweight="bold")
    ax1.set_ylabel("Percentage Change (%)")
    ax1.bar_label(bars, fmt='{:+.2f}%', padding=3)
    
    # 2. Post-COVID impact
    ax2 = axes[1]
    post_changes = pd.Series({
        "San Francisco": sf_post_change,
        "Oakland": oak_post_change
    })
    colors = ["red" if x < 0 else "green" for x in post_changes.values]
    bars = ax2.bar(post_changes.index, post_changes.values, color=colors)
    ax2.axhline(y=0, color="black", linestyle="-")
    ax2.set_title("Post-COVID Period Change from Pre-COVID", fontweight="bold")
    ax2.set_ylabel("Percentage Change (%)")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.bar_label(bars, fmt='{:+.2f}%', padding=3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "combined_period_impact.png", dpi=300, bbox_inches="tight")
    print(f"\nSaved period impact plot: {OUTPUT_DIR / 'combined_period_impact.png'}")
    plt.close()

def hourly_pattern_comparison(sf_df, oak_df):
    """Compare hourly crime patterns between cities."""
    print("\n" + "="*60)
    print("HOURLY PATTERN COMPARISON")
    print("="*60)
    
    sf_df["hour"] = sf_df["datetime"].dt.hour
    oak_df["hour"] = oak_df["datetime"].dt.hour
    
    sf_hourly = sf_df.groupby("hour").size()
    oak_hourly = oak_df.groupby("hour").size()
    
    # Normalize to percentages for comparison
    sf_hourly_pct = (sf_hourly / sf_hourly.sum()) * 100
    oak_hourly_pct = (oak_hourly / oak_hourly.sum()) * 100
    
    # Visualization
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    
    ax.plot(sf_hourly_pct.index, sf_hourly_pct.values, 
           marker="o", label="San Francisco", color="blue")
    ax.plot(oak_hourly_pct.index, oak_hourly_pct.values, 
           marker="o", label="Oakland", color="red")
    ax.set_title("Hourly Crime Distribution Comparison (Normalized)", fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Percentage of Total Incidents")
    ax.set_xticks(range(0, 24, 2))
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "combined_hourly_patterns.png", dpi=300, bbox_inches="tight")
    print(f"\nSaved hourly pattern plot: {OUTPUT_DIR / 'combined_hourly_patterns.png'}")
    plt.close()

def generate_combined_report(sf_df, oak_df):
    """Generate a combined summary report."""
    report_path = OUTPUT_DIR / "combined_analysis_summary.txt"
    
    with open(report_path, "w") as f:
        f.write("="*60 + "\n")
        f.write("SAN FRANCISCO vs OAKLAND CRIME DATA COMPARISON\n")
        f.write("="*60 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("DATASET OVERVIEW\n")
        f.write("-"*60 + "\n")
        f.write(f"San Francisco records: {len(sf_df):,}\n")
        f.write(f"Oakland records: {len(oak_df):,}\n")
        f.write(f"Total records: {len(sf_df) + len(oak_df):,}\n\n")
        
        f.write("DATE RANGES\n")
        f.write("-"*60 + "\n")
        f.write(f"San Francisco: {sf_df['date'].min()} to {sf_df['date'].max()}\n")
        f.write(f"Oakland: {oak_df['date'].min()} to {oak_df['date'].max()}\n\n")
        
        f.write("PERIOD BREAKDOWN\n")
        f.write("-"*60 + "\n")
        f.write("San Francisco:\n")
        sf_periods = sf_df.groupby("period_label").size()
        for period, count in sf_periods.items():
            pct = (count / len(sf_df)) * 100
            f.write(f"  {period:10s}: {count:8,} ({pct:5.2f}%)\n")
        
        f.write("\nOakland:\n")
        oak_periods = oak_df.groupby("period_label").size()
        for period, count in oak_periods.items():
            pct = (count / len(oak_df)) * 100
            f.write(f"  {period:10s}: {count:8,} ({pct:5.2f}%)\n")
        
        # Calculate percentage changes
        sf_pre = len(sf_df[sf_df["period_label"] == "pre"])
        sf_covid = len(sf_df[sf_df["period_label"] == "covid"])
        sf_post = len(sf_df[sf_df["period_label"] == "post"])
        
        oak_pre = len(oak_df[oak_df["period_label"] == "pre"])
        oak_covid = len(oak_df[oak_df["period_label"] == "covid"])
        oak_post = len(oak_df[oak_df["period_label"] == "post"])
        
        sf_covid_change = ((sf_covid - sf_pre) / sf_pre) * 100
        sf_post_change = ((sf_post - sf_pre) / sf_pre) * 100
        oak_covid_change = ((oak_covid - oak_pre) / oak_pre) * 100
        oak_post_change = ((oak_post - oak_pre) / oak_pre) * 100
        
        f.write("\nPERIOD IMPACT (Change from Pre-COVID)\n")
        f.write("-"*60 + "\n")
        f.write("San Francisco:\n")
        f.write(f"  COVID period: {sf_covid_change:+.2f}%\n")
        f.write(f"  Post-COVID period: {sf_post_change:+.2f}%\n")
        f.write("\nOakland:\n")
        f.write(f"  COVID period: {oak_covid_change:+.2f}%\n")
        f.write(f"  Post-COVID period: {oak_post_change:+.2f}%\n")
    
    print(f"\nSaved combined summary report: {report_path}")

def main():
    """Run all combined analyses."""
    sf_df, oak_df = load_data()
    print(f"Loaded {len(sf_df):,} SF records and {len(oak_df):,} Oakland records")
    
    city_comparison(sf_df, oak_df)
    period_impact_comparison(sf_df, oak_df)
    hourly_pattern_comparison(sf_df, oak_df)
    generate_combined_report(sf_df, oak_df)
    
    print("\n" + "="*60)
    print("Combined analysis complete! Check the 'output' directory for results.")
    print("="*60)

if __name__ == "__main__":
    main()

