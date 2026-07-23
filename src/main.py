from extract import extract_data
from load import load_data, load_to_database
from logger import get_logger
from transform import transform_age_data, transform_race_data
from utils import validate_data


logger = get_logger(__name__)


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
    """
    Run the complete homelessness ETL pipeline.
    """

    logger.info("ETL pipeline started.")

    try:
        logger.info("Step 1: Extracting datasets.")

        datasets = extract_data()

        age_raw = datasets["age"]
        race_raw = datasets["race"]

        logger.info(
            "Age rows loaded: %s",
            len(age_raw),
        )

        logger.info(
            "Race rows loaded: %s",
            len(race_raw),
        )

        logger.info("Step 2: Transforming age data.")

        age_cleaned = transform_age_data(age_raw)

        logger.info(
            "Age rows after cleaning: %s",
            len(age_cleaned),
        )

        logger.info("Step 3: Validating age data.")

        validate_data(
            age_cleaned,
            AGE_REQUIRED_COLUMNS,
            "Age dataset",
        )

        logger.info("Age dataset validation passed.")

        logger.info("Step 4: Transforming race data.")

        race_cleaned = transform_race_data(race_raw)

        logger.info(
            "Race rows after cleaning: %s",
            len(race_cleaned),
        )

        logger.info("Step 5: Validating race data.")

        validate_data(
            race_cleaned,
            RACE_REQUIRED_COLUMNS,
            "Race dataset",
        )

        logger.info("Race dataset validation passed.")

        logger.info("Step 6: Loading processed CSV files.")

        load_data(
            age_cleaned,
            "homelessness_by_age_cleaned.csv",
        )

        load_data(
            race_cleaned,
            "homelessness_by_race_cleaned.csv",
        )

        logger.info("Step 7: Loading datasets into SQLite.")

        load_to_database(
            age_cleaned,
            "homelessness_by_age",
        )

        load_to_database(
            race_cleaned,
            "homelessness_by_race",
        )

        logger.info("ETL pipeline completed successfully.")

    except Exception:
        logger.exception("ETL pipeline failed.")
        raise


if __name__ == "__main__":
    main()