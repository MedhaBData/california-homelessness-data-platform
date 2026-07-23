import pandas as pd


def validate_data(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> None:
    """
    Perform reusable data-quality checks.
    """

    # Check required columns
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name}: Missing columns: {missing_columns}"
        )

    # Check whether the dataset is empty
    if df.empty:
        raise ValueError(
            f"{dataset_name}: Dataset is empty."
        )

    # Check required columns for missing values
    missing_values = df[required_columns].isnull().sum()

    if missing_values.sum() > 0:
        raise ValueError(
            f"{dataset_name}: Missing values found:\n"
            f"{missing_values}"
        )

    # Check for negative homelessness counts
    negative_counts = (
        df["experiencing_homelessness_cnt"] < 0
    ).sum()

    if negative_counts > 0:
        raise ValueError(
            f"{dataset_name}: Found {negative_counts} "
            "negative homelessness counts."
        )

    # Check for reasonable calendar years
    invalid_years = (
        (df["calendar_year"] < 2000)
        | (df["calendar_year"] > 2100)
    ).sum()

    if invalid_years > 0:
        raise ValueError(
            f"{dataset_name}: Found {invalid_years} invalid years."
        )

    print(f"{dataset_name} validation passed.")