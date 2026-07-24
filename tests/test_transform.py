import pandas as pd

from src.data_quality import calculate_data_quality_metrics
from src.transform import transform_age_data, transform_race_data


def test_transform_age_data_removes_invalid_counts():
    """
    Verify that invalid homelessness counts such as '*'
    are converted to missing values and removed.
    """

    dataframe = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023, 2023],
            "LOCATION_ID": [1, 2],
            "LOCATION": ["Los Angeles", "San Diego"],
            "AGE_GROUP_PUBLIC": ["18–24", "25–34"],
            "EXPERIENCING_HOMELESSNESS_CNT": ["100", "*"],
        }
    )

    result = transform_age_data(dataframe)

    assert len(result) == 1
    assert result.iloc[0]["experiencing_homelessness_cnt"] == 100


def test_transform_age_data_removes_duplicates():
    """
    Verify that duplicate age records are removed.
    """

    dataframe = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023, 2023],
            "LOCATION_ID": [1, 1],
            "LOCATION": ["Los Angeles", "Los Angeles"],
            "AGE_GROUP_PUBLIC": ["18–24", "18–24"],
            "EXPERIENCING_HOMELESSNESS_CNT": [100, 100],
        }
    )

    result = transform_age_data(dataframe)

    assert len(result) == 1


def test_transform_race_data_renames_columns():
    """
    Verify that raw race-dataset columns are renamed
    to the project's standardized column names.
    """

    dataframe = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023],
            "LOCATION_ID": [1],
            "RACE_ETHNICITY": ["White"],
            "ALONE_OR_IN_COMBINATION": ["Race alone"],
            "CNT": [250],
        }
    )

    result = transform_race_data(dataframe)

    expected_columns = [
        "calendar_year",
        "location_id",
        "race",
        "race_alone_or_in_combination",
        "experiencing_homelessness_cnt",
    ]

    assert list(result.columns) == expected_columns
    assert result.iloc[0]["race"] == "White"
    assert result.iloc[0]["experiencing_homelessness_cnt"] == 250


def test_transform_race_data_removes_duplicates():
    """
    Verify that duplicate race records are removed.
    """

    dataframe = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023, 2023],
            "LOCATION_ID": [1, 1],
            "RACE_ETHNICITY": ["White", "White"],
            "ALONE_OR_IN_COMBINATION": [
                "Race alone",
                "Race alone",
            ],
            "CNT": [250, 250],
        }
    )

    result = transform_race_data(dataframe)

    assert len(result) == 1


def test_data_quality_detects_missing_values():
    """
    Verify that the data-quality checker detects missing values.
    """

    dataframe = pd.DataFrame(
        {
            "calendar_year": [2024, 2024],
            "experiencing_homelessness_cnt": [100, None],
        }
    )

    metrics = calculate_data_quality_metrics(
        dataframe,
        "Test dataset",
    )

    missing_metric = next(
        metric
        for metric in metrics
        if metric["metric"] == "Missing values"
    )

    assert missing_metric["value"] == 1
    assert missing_metric["status"] == "FAIL"


def test_data_quality_passes_clean_data():
    """
    Verify that a clean dataset receives an overall PASS status.
    """

    dataframe = pd.DataFrame(
        {
            "calendar_year": [2023, 2024],
            "location_id": [1, 2],
            "experiencing_homelessness_cnt": [100, 200],
        }
    )

    metrics = calculate_data_quality_metrics(
        dataframe,
        "Test dataset",
    )

    overall_status = next(
        metric
        for metric in metrics
        if metric["metric"] == "Overall dataset status"
    )

    assert overall_status["value"] == "PASS"
    assert overall_status["status"] == "PASS"