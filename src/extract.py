from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")

DATA_FILES = {
    "age": RAW_DATA_DIR / "homelessness_by_age.csv",
    "race": RAW_DATA_DIR / "homelessness_by_race.csv",
}


def extract_data():
    """
    Read all raw homelessness CSV files.

    Returns:
        A dictionary containing one DataFrame for each dataset.
    """

    datasets = {}

    for dataset_name, file_path in DATA_FILES.items():
        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        datasets[dataset_name] = pd.read_csv(file_path)

    return datasets