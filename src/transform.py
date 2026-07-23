import pandas as pd


def transform_age_data(df):
    """
    Clean and transform the homelessness-by-age dataset.
    """

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Clean text columns
    df["location"] = (
        df["location"]
        .astype("string")
        .str.strip()
    )

    df["age_group_public"] = (
        df["age_group_public"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric columns safely
    df["calendar_year"] = pd.to_numeric(
        df["calendar_year"],
        errors="coerce",
    )

    df["experiencing_homelessness_cnt"] = pd.to_numeric(
        df["experiencing_homelessness_cnt"],
        errors="coerce",
    )

    # Remove rows with invalid essential values
    df = df.dropna(
        subset=[
            "calendar_year",
            "location_id",
            "location",
            "age_group_public",
            "experiencing_homelessness_cnt",
        ]
    )

    # Convert valid numeric columns to integers
    df["calendar_year"] = df["calendar_year"].astype(int)

    df["experiencing_homelessness_cnt"] = (
        df["experiencing_homelessness_cnt"]
        .astype(int)
    )

    # Sort records
    df = df.sort_values(
        by=[
            "calendar_year",
            "location",
            "age_group_public",
        ]
    )

    return df


def transform_race_data(df):
    """
    Clean and transform the homelessness-by-race dataset.
    """

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Rename columns to consistent project names
    df = df.rename(
        columns={
            "race_ethnicity": "race",
            "alone_or_in_combination":
                "race_alone_or_in_combination",
            "cnt": "experiencing_homelessness_cnt",
        }
    )

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Clean text columns
    text_columns = [
        "location_id",
        "race",
        "race_alone_or_in_combination",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Convert numeric columns safely
    df["calendar_year"] = pd.to_numeric(
        df["calendar_year"],
        errors="coerce",
    )

    df["experiencing_homelessness_cnt"] = pd.to_numeric(
        df["experiencing_homelessness_cnt"],
        errors="coerce",
    )

    # Remove rows with invalid essential values
    df = df.dropna(
        subset=[
            "calendar_year",
            "location_id",
            "race",
            "race_alone_or_in_combination",
            "experiencing_homelessness_cnt",
        ]
    )

    # Convert valid numeric columns to integers
    df["calendar_year"] = df["calendar_year"].astype(int)

    df["experiencing_homelessness_cnt"] = (
        df["experiencing_homelessness_cnt"]
        .astype(int)
    )

    # Sort records
    df = df.sort_values(
        by=[
            "calendar_year",
            "location_id",
            "race",
        ]
    )

    return df