from pathlib import Path

import pandas as pd


REPORTS_DIR = Path("reports")
REPORT_FILE = REPORTS_DIR / "data_quality_report.csv"


def calculate_data_quality_metrics(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> list[dict]:
    """
    Calculate basic data-quality metrics for a dataset.
    """

    total_rows = len(dataframe)
    duplicate_rows = int(dataframe.duplicated().sum())
    missing_values = int(dataframe.isna().sum().sum())

    invalid_years = 0
    if "calendar_year" in dataframe.columns:
        invalid_years = int(
            (
                (dataframe["calendar_year"] < 2000)
                | (dataframe["calendar_year"] > 2100)
            ).sum()
        )

    negative_counts = 0
    if "experiencing_homelessness_cnt" in dataframe.columns:
        negative_counts = int(
            (
                dataframe["experiencing_homelessness_cnt"] < 0
            ).sum()
        )

    status = "PASS"

    if (
        duplicate_rows > 0
        or missing_values > 0
        or invalid_years > 0
        or negative_counts > 0
    ):
        status = "FAIL"

    return [
        {
            "dataset": dataset_name,
            "metric": "Total rows",
            "value": total_rows,
            "status": "INFO",
        },
        {
            "dataset": dataset_name,
            "metric": "Duplicate rows",
            "value": duplicate_rows,
            "status": "PASS" if duplicate_rows == 0 else "FAIL",
        },
        {
            "dataset": dataset_name,
            "metric": "Missing values",
            "value": missing_values,
            "status": "PASS" if missing_values == 0 else "FAIL",
        },
        {
            "dataset": dataset_name,
            "metric": "Invalid years",
            "value": invalid_years,
            "status": "PASS" if invalid_years == 0 else "FAIL",
        },
        {
            "dataset": dataset_name,
            "metric": "Negative homelessness counts",
            "value": negative_counts,
            "status": "PASS" if negative_counts == 0 else "FAIL",
        },
        {
            "dataset": dataset_name,
            "metric": "Overall dataset status",
            "value": status,
            "status": status,
        },
    ]


def create_data_quality_report(
    age_dataframe: pd.DataFrame,
    race_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create and save a combined data-quality report.
    """

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    age_metrics = calculate_data_quality_metrics(
        age_dataframe,
        "Age dataset",
    )

    race_metrics = calculate_data_quality_metrics(
        race_dataframe,
        "Race dataset",
    )

    report_dataframe = pd.DataFrame(
        age_metrics + race_metrics
    )

    report_dataframe.to_csv(
        REPORT_FILE,
        index=False,
    )

    return report_dataframe