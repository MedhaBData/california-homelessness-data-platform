import pandas as pd

from src.transform import transform_data


def test_transform_data_removes_invalid_counts():
    sample_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023, 2023, 2023],
            "LOCATION_ID": ["CA-500", "CA-501", "CA-502"],
            "LOCATION": [
                "Location A",
                "Location B",
                "Location C",
            ],
            "AGE_GROUP_PUBLIC": [
                "18-24",
                "25-34",
                "35-44",
            ],
            "EXPERIENCING_HOMELESSNESS_CNT": [
                "100",
                "*",
                "250",
            ],
        }
    )

    result = transform_data(sample_data)

    assert len(result) == 2
    assert result["experiencing_homelessness_cnt"].tolist() == [100, 250]


def test_transform_data_removes_duplicates():
    sample_data = pd.DataFrame(
        {
            "CALENDAR_YEAR": [2023, 2023],
            "LOCATION_ID": ["CA-500", "CA-500"],
            "LOCATION": ["Location A", "Location A"],
            "AGE_GROUP_PUBLIC": ["18-24", "18-24"],
            "EXPERIENCING_HOMELESSNESS_CNT": ["100", "100"],
        }
    )

    result = transform_data(sample_data)

    assert len(result) == 1