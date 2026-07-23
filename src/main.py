from extract import extract_data
from load import load_data
from transform import transform_age_data, transform_race_data
from utils import validate_data


AGE_REQUIRED_COLUMNS = [
    "calendar_year",
    "location_id",
    "location",
    "age_group_public",
    "experiencing_homelessness_cnt",
]

RACE_REQUIRED_COLUMNS = [
    "calendar_year",
    "location_id",
    "race",
    "race_alone_or_in_combination",
    "experiencing_homelessness_cnt",
]


def main():
    print("Step 1: Extracting datasets...")
    datasets = extract_data()

    age_raw = datasets["age"]
    race_raw = datasets["race"]

    print("Age rows loaded:", len(age_raw))
    print("Race rows loaded:", len(race_raw))

    print("\nStep 2: Transforming age data...")
    age_cleaned = transform_age_data(age_raw)
    print("Age rows after cleaning:", len(age_cleaned))

    print("\nStep 3: Validating age data...")
    validate_data(
        age_cleaned,
        AGE_REQUIRED_COLUMNS,
        "Age dataset",
    )

    print("\nStep 4: Transforming race data...")
    race_cleaned = transform_race_data(race_raw)
    print("Race rows after cleaning:", len(race_cleaned))

    print("\nStep 5: Validating race data...")
    validate_data(
        race_cleaned,
        RACE_REQUIRED_COLUMNS,
        "Race dataset",
    )

    print("\nStep 6: Loading processed datasets...")

    load_data(
        age_cleaned,
        "homelessness_by_age_cleaned.csv",
    )

    load_data(
        race_cleaned,
        "homelessness_by_race_cleaned.csv",
    )

    print("\nETL pipeline completed successfully!")


if __name__ == "__main__":
    main()