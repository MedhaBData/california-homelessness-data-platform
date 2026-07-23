import pandas as pd

from src.transform import transform_age_data, transform_race_data


def test_transform_age_removes_invalid_counts():
    input_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2024, 2024],
            "LOCATION_ID": ["001", "002"],
            "LOCATION": ["Los Angeles", "San Diego"],
            "AGE_GROUP_PUBLIC": ["18–24", "25–34"],
            "EXPERIENCING_HOMELESSNESS_CNT": ["100", "*"],
        }
    )

    result = transform_age_data(input_data)

    assert len(result) == 1
    assert result.iloc[0]["experiencing_homelessness_cnt"] == 100


def test_transform_age_removes_duplicates():
    input_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2024, 2024],
            "LOCATION_ID": ["001", "001"],
            "LOCATION": ["Los Angeles", "Los Angeles"],
            "AGE_GROUP_PUBLIC": ["18–24", "18–24"],
            "EXPERIENCING_HOMELESSNESS_CNT": ["100", "100"],
        }
    )

    result = transform_age_data(input_data)

    assert len(result) == 1


def test_transform_race_renames_and_cleans_columns():
    input_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2024, 2024],
            "LOCATION_ID": ["001", "002"],
            "RACE_ETHNICITY": ["White", "Black"],
            "ALONE_OR_IN_COMBINATION": ["Alone", "Combination"],
            "CNT": ["150", "*"],
        }
    )

    result = transform_race_data(input_data)

    assert len(result) == 1
    assert "race" in result.columns
    assert "race_alone_or_in_combination" in result.columns
    assert "experiencing_homelessness_cnt" in result.columns
    assert result.iloc[0]["experiencing_homelessness_cnt"] == 150


def test_transform_race_removes_duplicates():
    input_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2024, 2024],
            "LOCATION_ID": ["001", "001"],
            "RACE_ETHNICITY": ["White", "White"],
            "ALONE_OR_IN_COMBINATION": ["Alone", "Alone"],
            "CNT": ["150", "150"],
        }
    )

    result = transform_race_data(input_data)

    assert len(result) == 1