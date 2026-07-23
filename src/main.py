from extract import extract_data
from transform import transform_data
from load import load_data


def main():

    print("Step 1: Extracting data...")
    df = extract_data()

    print("Rows loaded:", len(df))

    print("Step 2: Transforming data...")
    df = transform_data(df)

    print("Rows after cleaning:", len(df))

    print("Step 3: Loading cleaned data...")
    load_data(df)

    print("ETL Pipeline Completed Successfully!")


if __name__ == "__main__":
    main()