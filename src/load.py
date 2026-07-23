from pathlib import Path

import pandas as pd


PROCESSED_DATA_DIR = Path("data/processed")


def load_data(
    df: pd.DataFrame,
    output_filename: str,
):
    """
    Save a cleaned DataFrame to the processed folder.
    """

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PROCESSED_DATA_DIR /
        output_filename
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved: {output_path}"
    )