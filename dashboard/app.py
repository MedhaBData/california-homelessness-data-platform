from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


DATABASE_PATH = Path("data/homelessness.db")


st.set_page_config(
    page_title="California Homelessness Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def run_query(query: str, parameters: tuple = ()) -> pd.DataFrame:
    """
    Execute a SQL query against the SQLite database.
    """

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run 'python src/main.py' first."
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        dataframe = pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )

    return dataframe


def dataframe_to_csv(dataframe: pd.DataFrame) -> bytes:
    """
    Convert a DataFrame to CSV bytes for download.
    """

    return dataframe.to_csv(index=False).encode("utf-8")


st.title("California Homelessness Analytics Dashboard")

st.write(
    "Explore homelessness trends by year, age group, "
    "race and location using data processed through "
    "a Python ETL pipeline and stored in SQLite."
)


# -------------------------------------------------
# Sidebar filters
# -------------------------------------------------

st.sidebar.header("Dashboard Filters")


years_query = """
    SELECT DISTINCT calendar_year
    FROM homelessness_by_age
    ORDER BY calendar_year;
"""

locations_query = """
    SELECT DISTINCT location
    FROM homelessness_by_age
    ORDER BY location;
"""

age_groups_query = """
    SELECT DISTINCT age_group_public
    FROM homelessness_by_age
    ORDER BY age_group_public;
"""

races_query = """
    SELECT DISTINCT race
    FROM homelessness_by_race
    ORDER BY race;
"""


years = run_query(years_query)["calendar_year"].tolist()
locations = run_query(locations_query)["location"].tolist()
age_groups = run_query(age_groups_query)["age_group_public"].tolist()
races = run_query(races_query)["race"].tolist()


selected_year = st.sidebar.selectbox(
    "Select year",
    options=["All years"] + years,
)

selected_location = st.sidebar.selectbox(
    "Select location",
    options=["All locations"] + locations,
)

selected_age_group = st.sidebar.selectbox(
    "Select age group",
    options=["All age groups"] + age_groups,
)

selected_race = st.sidebar.selectbox(
    "Select race or ethnicity",
    options=["All races"] + races,
)


# -------------------------------------------------
# Build age-data filter
# -------------------------------------------------

age_conditions = []
age_parameters = []

if selected_year != "All years":
    age_conditions.append("calendar_year = ?")
    age_parameters.append(selected_year)

if selected_location != "All locations":
    age_conditions.append("location = ?")
    age_parameters.append(selected_location)

if selected_age_group != "All age groups":
    age_conditions.append("age_group_public = ?")
    age_parameters.append(selected_age_group)

age_where_clause = ""

if age_conditions:
    age_where_clause = "WHERE " + " AND ".join(age_conditions)


# -------------------------------------------------
# Build race-data filter
# -------------------------------------------------

race_conditions = []
race_parameters = []

if selected_year != "All years":
    race_conditions.append("calendar_year = ?")
    race_parameters.append(selected_year)

if selected_race != "All races":
    race_conditions.append("race = ?")
    race_parameters.append(selected_race)

race_where_clause = ""

if race_conditions:
    race_where_clause = "WHERE " + " AND ".join(race_conditions)


# -------------------------------------------------
# Run filtered queries
# -------------------------------------------------

age_filtered_query = f"""
    SELECT
        calendar_year,
        location,
        age_group_public,
        experiencing_homelessness_cnt
    FROM homelessness_by_age
    {age_where_clause}
    ORDER BY calendar_year, location, age_group_public;
"""

race_filtered_query = f"""
    SELECT
        calendar_year,
        location_id,
        race,
        race_alone_or_in_combination,
        experiencing_homelessness_cnt
    FROM homelessness_by_race
    {race_where_clause}
    ORDER BY calendar_year, race;
"""


age_filtered_data = run_query(
    age_filtered_query,
    tuple(age_parameters),
)

race_filtered_data = run_query(
    race_filtered_query,
    tuple(race_parameters),
)


# -------------------------------------------------
# KPI metrics
# -------------------------------------------------

total_homelessness = int(
    age_filtered_data["experiencing_homelessness_cnt"].sum()
)

location_count = age_filtered_data["location"].nunique()
age_group_count = age_filtered_data["age_group_public"].nunique()
race_group_count = race_filtered_data["race"].nunique()


metric_1, metric_2, metric_3, metric_4 = st.columns(4)

with metric_1:
    st.metric(
        "Total homelessness count",
        f"{total_homelessness:,}",
    )

with metric_2:
    st.metric(
        "Locations included",
        location_count,
    )

with metric_3:
    st.metric(
        "Age groups included",
        age_group_count,
    )

with metric_4:
    st.metric(
        "Race groups included",
        race_group_count,
    )


st.divider()


# -------------------------------------------------
# Filtered trend chart
# -------------------------------------------------

st.subheader("Homelessness trend over time")

trend_data = (
    age_filtered_data
    .groupby(
        "calendar_year",
        as_index=False,
    )["experiencing_homelessness_cnt"]
    .sum()
)

trend_chart_data = trend_data.set_index("calendar_year")

st.line_chart(
    trend_chart_data["experiencing_homelessness_cnt"]
)


# -------------------------------------------------
# Age and location charts
# -------------------------------------------------

left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Homelessness by age group")

    age_group_data = (
        age_filtered_data
        .groupby(
            "age_group_public",
            as_index=False,
        )["experiencing_homelessness_cnt"]
        .sum()
        .sort_values(
            "experiencing_homelessness_cnt",
            ascending=False,
        )
    )

    age_group_chart_data = age_group_data.set_index(
        "age_group_public"
    )

    st.bar_chart(
        age_group_chart_data[
            "experiencing_homelessness_cnt"
        ]
    )

with right_column:
    st.subheader("Top 10 locations")

    location_data = (
        age_filtered_data
        .groupby(
            "location",
            as_index=False,
        )["experiencing_homelessness_cnt"]
        .sum()
        .sort_values(
            "experiencing_homelessness_cnt",
            ascending=False,
        )
        .head(10)
    )

    location_chart_data = location_data.set_index("location")

    st.bar_chart(
        location_chart_data[
            "experiencing_homelessness_cnt"
        ]
    )


st.divider()


# -------------------------------------------------
# Race chart
# -------------------------------------------------

st.subheader("Homelessness by race and ethnicity")

race_group_data = (
    race_filtered_data
    .groupby(
        "race",
        as_index=False,
    )["experiencing_homelessness_cnt"]
    .sum()
    .sort_values(
        "experiencing_homelessness_cnt",
        ascending=False,
    )
)

race_chart_data = race_group_data.set_index("race")

st.bar_chart(
    race_chart_data[
        "experiencing_homelessness_cnt"
    ]
)


st.divider()


# -------------------------------------------------
# Data tables and downloads
# -------------------------------------------------

st.subheader("Explore and download filtered data")

tab_1, tab_2 = st.tabs(
    [
        "Age dataset",
        "Race dataset",
    ]
)

with tab_1:
    st.dataframe(
        age_filtered_data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download filtered age data",
        data=dataframe_to_csv(age_filtered_data),
        file_name="filtered_homelessness_by_age.csv",
        mime="text/csv",
    )

with tab_2:
    st.dataframe(
        race_filtered_data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download filtered race data",
        data=dataframe_to_csv(race_filtered_data),
        file_name="filtered_homelessness_by_race.csv",
        mime="text/csv",
    )


st.caption(
    "Built with Python, pandas, SQLite, SQL and Streamlit."
)