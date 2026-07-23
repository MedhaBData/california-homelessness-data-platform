from pathlib import Path


OUTPUT_FILE = Path(
    "data/processed/homelessness_by_age_cleaned.csv"
)


def load_data(df):
    """
    Save cleaned data to CSV.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"✅ Saved cleaned data to {OUTPUT_FILE}")