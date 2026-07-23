from time import perf_counter

from data_quality import create_data_quality_report
from extract import extract_data
from load import load_data, load_to_database
from logger import get_logger
from monitoring import save_pipeline_run
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

    start_time = perf_counter()
    age_row_count = 0
    race_row_count = 0

    logger.info("==========================================")
    logger.info("California Homelessness ETL Pipeline Started")
    logger.info("==========================================")

    try:
        logger.info("Step 1: Extracting datasets.")

        datasets = extract_data()

        age_raw = datasets["age"]
        race_raw = datasets["race"]

        logger.info(
            "Age dataset extracted: %s rows",
            len(age_raw),
        )

        logger.info(
            "Race dataset extracted: %s rows",
            len(race_raw),
        )

        logger.info("Step 2: Transforming age dataset.")

        age_cleaned = transform_age_data(age_raw)
        age_row_count = len(age_cleaned)

        logger.info(
            "Age dataset cleaned: %s rows",
            age_row_count,
        )

        logger.info("Transforming race dataset.")

        race_cleaned = transform_race_data(race_raw)
        race_row_count = len(race_cleaned)

        logger.info(
            "Race dataset cleaned: %s rows",
            race_row_count,
        )

        logger.info("Step 3: Validating datasets.")

        validate_data(
            age_cleaned,
            AGE_REQUIRED_COLUMNS,
            "Age dataset",
        )

        validate_data(
            race_cleaned,
            RACE_REQUIRED_COLUMNS,
            "Race dataset",
        )

        logger.info("Validation completed successfully.")

        logger.info("Step 4: Saving cleaned CSV files.")

        load_data(
            age_cleaned,
            "homelessness_by_age_cleaned.csv",
        )

        load_data(
            race_cleaned,
            "homelessness_by_race_cleaned.csv",
        )

        logger.info("Processed CSV files saved.")

        logger.info("Step 5: Loading SQLite database.")

        load_to_database(
            age_cleaned,
            "homelessness_by_age",
        )

        load_to_database(
            race_cleaned,
            "homelessness_by_race",
        )

        logger.info("SQLite database updated.")

        logger.info("Step 6: Creating data quality report.")

        quality_report = create_data_quality_report(
            age_cleaned,
            race_cleaned,
        )

        logger.info(
            "Generated %s quality metrics.",
            len(quality_report),
        )

        duration_seconds = perf_counter() - start_time

        save_pipeline_run(
            status="PASS",
            age_rows=age_row_count,
            race_rows=race_row_count,
            duration_seconds=duration_seconds,
        )

        logger.info(
            "Pipeline run history updated."
        )

        logger.info("==========================================")
        logger.info("ETL Pipeline Completed Successfully")
        logger.info("==========================================")

    except Exception as error:
        duration_seconds = perf_counter() - start_time

        save_pipeline_run(
            status="FAIL",
            age_rows=age_row_count,
            race_rows=race_row_count,
            duration_seconds=duration_seconds,
            error_message=str(error),
        )

        logger.exception("ETL Pipeline Failed")
        raise


if __name__ == "__main__":
    main()