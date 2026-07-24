from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ANALYSIS_DATA_DIR = Path("data/analysis")
CHART_OUTPUT_DIR = Path("data/charts")


def load_analysis_file(filename: str) -> pd.DataFrame:
    """
    Load a generated analysis CSV file.
    """

    file_path = ANALYSIS_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Analysis file not found: {file_path}. "
            "Run 'python src/analyze.py' first."
        )

    return pd.read_csv(file_path)


def save_chart(filename: str) -> None:
    """
    Save the current Matplotlib chart.
    """

    CHART_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CHART_OUTPUT_DIR / filename

    plt.tight_layout()
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(f"Saved chart: {output_path}")


def create_yearly_trend_chart() -> None:
    """
    Create a line chart showing homelessness totals by year.
    """

    dataframe = load_analysis_file(
        "yearly_homelessness_totals.csv"
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        dataframe["calendar_year"],
        dataframe["total_homelessness_count"],
        marker="o",
    )

    plt.title("California Homelessness Count by Year")
    plt.xlabel("Calendar Year")
    plt.ylabel("Total Homelessness Count")
    plt.grid(True)

    save_chart("yearly_homelessness_trend.png")


def create_age_group_chart() -> None:
    """
    Create a bar chart showing homelessness totals by age group.
    """

    dataframe = load_analysis_file(
        "age_group_totals.csv"
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        dataframe["age_group_public"],
        dataframe["total_homelessness_count"],
    )

    plt.title("Homelessness Count by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Total Homelessness Count")
    plt.xticks(rotation=45, ha="right")

    save_chart("homelessness_by_age_group.png")


def create_top_locations_chart() -> None:
    """
    Create a horizontal bar chart for the top 10 locations.
    """

    dataframe = load_analysis_file(
        "top_10_locations.csv"
    )

    dataframe = dataframe.sort_values(
        by="total_homelessness_count"
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        dataframe["location"],
        dataframe["total_homelessness_count"],
    )

    plt.title("Top 10 California Locations by Homelessness Count")
    plt.xlabel("Total Homelessness Count")
    plt.ylabel("Location")

    save_chart("top_10_locations.png")


def create_race_chart() -> None:
    """
    Create a bar chart showing homelessness totals by race.
    """

    dataframe = load_analysis_file(
        "race_totals.csv"
    )

    plt.figure(figsize=(11, 7))

    plt.bar(
        dataframe["race"],
        dataframe["total_homelessness_count"],
    )

    plt.title("Homelessness Count by Race and Ethnicity")
    plt.xlabel("Race and Ethnicity")
    plt.ylabel("Total Homelessness Count")
    plt.xticks(rotation=45, ha="right")

    save_chart("homelessness_by_race.png")


def main():
    print("Creating charts...")

    create_yearly_trend_chart()
    create_age_group_chart()
    create_top_locations_chart()
    create_race_chart()

    print("\nAll charts created successfully!")


if __name__ == "__main__":
    main()