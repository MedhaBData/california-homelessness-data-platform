from pathlib import Path
import sqlite3

import pandas as pd


PROCESSED_DATA_DIR = Path("data/processed")
DATABASE_PATH = Path("data/homelessness.db")


def load_data(
    df: pd.DataFrame,
    output_filename: str,
) -> None:
    """
    Save a cleaned DataFrame as a CSV file.
    """

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = PROCESSED_DATA_DIR / output_filename

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"Saved: {output_path}")


def load_to_database(
    df: pd.DataFrame,
    table_name: str,
) -> None:
    """
    Load a cleaned DataFrame into a SQLite table.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
        )

    print(
        f"Loaded table '{table_name}' "
        f"into {DATABASE_PATH}"
    )