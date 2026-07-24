from pathlib import Path
import sqlite3

import pandas as pd


DATABASE_PATH = Path("data/homelessness.db")
ANALYSIS_OUTPUT_DIR = Path("data/analysis")


def run_query(query: str) -> pd.DataFrame:
    """
    Run a SQL query against the homelessness SQLite database.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run 'python src/main.py' first."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        result = pd.read_sql_query(
            query,
            connection,
        )

    return result


def save_result(
    dataframe: pd.DataFrame,
    filename: str,
) -> None:
    """
    Save an analysis result as a CSV file.
    """

    ANALYSIS_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = ANALYSIS_OUTPUT_DIR / filename

    dataframe.to_csv(
        output_path,
        index=False,
    )

    print(f"Saved analysis: {output_path}")


def main():
    print("Running SQL analysis...")

    yearly_totals_query = """
        SELECT
            calendar_year,
            SUM(experiencing_homelessness_cnt)
                AS total_homelessness_count
        FROM homelessness_by_age
        GROUP BY calendar_year
        ORDER BY calendar_year;
    """

    age_group_query = """
        SELECT
            age_group_public,
            SUM(experiencing_homelessness_cnt)
                AS total_homelessness_count
        FROM homelessness_by_age
        GROUP BY age_group_public
        ORDER BY total_homelessness_count DESC;
    """

    top_locations_query = """
        SELECT
            location,
            SUM(experiencing_homelessness_cnt)
                AS total_homelessness_count
        FROM homelessness_by_age
        GROUP BY location
        ORDER BY total_homelessness_count DESC
        LIMIT 10;
    """

    race_totals_query = """
        SELECT
            race,
            SUM(experiencing_homelessness_cnt)
                AS total_homelessness_count
        FROM homelessness_by_race
        GROUP BY race
        ORDER BY total_homelessness_count DESC;
    """

    yearly_totals = run_query(yearly_totals_query)
    age_group_totals = run_query(age_group_query)
    top_locations = run_query(top_locations_query)
    race_totals = run_query(race_totals_query)

    print("\nHomelessness totals by year:")
    print(yearly_totals.to_string(index=False))

    print("\nHomelessness totals by age group:")
    print(age_group_totals.to_string(index=False))

    print("\nTop 10 locations:")
    print(top_locations.to_string(index=False))

    print("\nHomelessness totals by race:")
    print(race_totals.to_string(index=False))

    save_result(
        yearly_totals,
        "yearly_homelessness_totals.csv",
    )

    save_result(
        age_group_totals,
        "age_group_totals.csv",
    )

    save_result(
        top_locations,
        "top_10_locations.csv",
    )

    save_result(
        race_totals,
        "race_totals.csv",
    )

    print("\nSQL analysis completed successfully!")


if __name__ == "__main__":
    main()