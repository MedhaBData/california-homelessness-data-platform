import pandas as pd


def transform_data(df):
    """
    Clean and transform the homelessness-by-age dataset.
    """

    # Work on a copy of the original DataFrame
    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Remove completely duplicated rows
    df = df.drop_duplicates()

    # Clean text columns
    df["location"] = df["location"].astype("string").str.strip()
    df["age_group_public"] = (
        df["age_group_public"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric columns safely.
    # Invalid values such as "*" become missing values.
    df["calendar_year"] = pd.to_numeric(
        df["calendar_year"],
        errors="coerce"
    )

    df["experiencing_homelessness_cnt"] = pd.to_numeric(
        df["experiencing_homelessness_cnt"],
        errors="coerce"
    )

    # Remove rows missing essential values
    df = df.dropna(
        subset=[
            "calendar_year",
            "location",
            "age_group_public",
            "experiencing_homelessness_cnt",
        ]
    )

    # Convert valid numeric values to integers
    df["calendar_year"] = df["calendar_year"].astype(int)

    df["experiencing_homelessness_cnt"] = (
        df["experiencing_homelessness_cnt"]
        .astype(int)
    )

    # Sort the cleaned dataset
    df = df.sort_values(
        by=[
            "calendar_year",
            "location",
            "age_group_public",
        ]
    )

    return df