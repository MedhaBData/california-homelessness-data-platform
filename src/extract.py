from pathlib import Path
import pandas as pd


RAW_FILE = Path("data/raw/homelessness_by_age.csv")


def extract_data():
    """
    Read the raw CSV file and return a DataFrame.
    """
    df = pd.read_csv(RAW_FILE)
    return df