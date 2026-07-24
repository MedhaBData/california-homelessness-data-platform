from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from map_utils import create_california_county_map


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="California Homelessness Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "data" / "homelessness.db"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATA_QUALITY_PATH = REPORTS_DIR / "data_quality_report.csv"
PIPELINE_HISTORY_PATH = REPORTS_DIR / "pipeline_run_history.csv"


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background-color: #111827;
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        .main-header {
            padding: 1.8rem;
            border-radius: 16px;
            background: linear-gradient(
                90deg,
                #155e75 0%,
                #0f766e 50%,
                #2a9d8f 100%
            );
            color: white;
            margin-bottom: 1.4rem;
        }

        .main-header h1 {
            margin: 0;
            font-size: 2.15rem;
            color: white;
        }

        .main-header p {
            margin-top: 0.7rem;
            margin-bottom: 0;
            font-size: 1rem;
            line-height: 1.7;
            color: white;
        }

        .section-title {
            margin-top: 1.4rem;
            margin-bottom: 0.8rem;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .insight-card {
            padding: 1rem 1.2rem;
            border-left: 5px solid #2a9d8f;
            border-radius: 8px;
            background-color: #ecfeff;
            color: #164e63;
            margin-bottom: 0.7rem;
            font-weight: 500;
        }

        .status-pass {
            padding: 0.8rem;
            border-radius: 8px;
            background-color: #dcfce7;
            color: #166534;
            font-weight: 700;
            text-align: center;
        }

        .status-fail {
            padding: 0.8rem;
            border-radius: 8px;
            background-color: #fee2e2;
            color: #991b1b;
            font-weight: 700;
            text-align: center;
        }

        div[data-testid="stMetric"] {
            background-color: #16212d;
            border: 1px solid #334155;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
        }

        div[data-testid="stMetric"] label {
            color: #cbd5e1 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        div[data-testid="stMetricDelta"] {
            color: #cbd5e1 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize dataframe column names.
    """
    normalized_df = dataframe.copy()

    normalized_df.columns = (
        normalized_df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    return normalized_df


def find_column(
    dataframe: pd.DataFrame,
    possible_names: list[str],
) -> str | None:
    """
    Return the first matching column name.
    """
    for column_name in possible_names:
        if column_name in dataframe.columns:
            return column_name

    return None


def convert_numeric(
    dataframe: pd.DataFrame,
    column_name: str | None,
) -> pd.DataFrame:
    """
    Convert a column to numeric safely.
    """
    converted_df = dataframe.copy()

    if column_name and column_name in converted_df.columns:
        converted_df[column_name] = pd.to_numeric(
            converted_df[column_name],
            errors="coerce",
        )

    return converted_df


def read_csv_safely(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV without crashing the dashboard.
    """
    if not file_path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_database_tables(
    database_path_string: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the age and race tables from SQLite.
    """
    database_path = Path(database_path_string)

    if not database_path.exists():
        return pd.DataFrame(), pd.DataFrame()

    try:
        with sqlite3.connect(database_path) as connection:
            age_data = pd.read_sql_query(
                "SELECT * FROM homelessness_by_age",
                connection,
            )

            race_data = pd.read_sql_query(
                "SELECT * FROM homelessness_by_race",
                connection,
            )

        return (
            normalize_columns(age_data),
            normalize_columns(race_data),
        )

    except Exception as error:
        st.error(f"Database loading error: {error}")
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def load_report(file_path_string: str) -> pd.DataFrame:
    """
    Load and normalize a report CSV.
    """
    file_path = Path(file_path_string)
    report_df = read_csv_safely(file_path)

    if report_df.empty:
        return report_df

    return normalize_columns(report_df)


def create_download_button(
    label: str,
    dataframe: pd.DataFrame,
    filename: str,
    key: str,
) -> None:
    """
    Create a CSV download button.
    """
    csv_data = dataframe.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=key,
        use_container_width=True,
    )


def format_number(value: float | int) -> str:
    """
    Format numeric values with commas.
    """
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def build_insights(
    age_dataframe: pd.DataFrame,
    race_dataframe: pd.DataFrame,
    age_year_column: str | None,
    age_category_column: str | None,
    age_location_column: str | None,
    age_count_column: str | None,
    race_category_column: str | None,
    race_count_column: str | None,
) -> list[str]:
    """
    Generate automatic analytical insights.
    """
    insights: list[str] = []

    if (
        age_count_column
        and age_count_column in age_dataframe.columns
        and not age_dataframe.empty
    ):
        total_population = age_dataframe[age_count_column].sum()

        if (
            total_population > 0
            and age_location_column
            and age_location_column in age_dataframe.columns
        ):
            location_totals = (
                age_dataframe.groupby(age_location_column)[age_count_column]
                .sum()
                .sort_values(ascending=False)
            )

            if not location_totals.empty:
                top_location = str(location_totals.index[0])
                top_location_value = float(location_totals.iloc[0])

                contribution = (
                    top_location_value / total_population
                ) * 100

                insights.append(
                    f"{top_location} has the highest recorded total and "
                    f"represents approximately {contribution:.1f}% of the "
                    f"selected population."
                )

        if (
            age_category_column
            and age_category_column in age_dataframe.columns
        ):
            age_totals = (
                age_dataframe.groupby(age_category_column)[age_count_column]
                .sum()
                .sort_values(ascending=False)
            )

            if not age_totals.empty:
                insights.append(
                    f"The largest age category is "
                    f"{age_totals.index[0]}, with "
                    f"{format_number(age_totals.iloc[0])} people."
                )

        if (
            age_year_column
            and age_year_column in age_dataframe.columns
            and age_dataframe[age_year_column].nunique() >= 2
        ):
            yearly_totals = (
                age_dataframe.groupby(age_year_column)[age_count_column]
                .sum()
                .sort_index()
            )

            first_year = int(yearly_totals.index[0])
            latest_year = int(yearly_totals.index[-1])

            first_value = float(yearly_totals.iloc[0])
            latest_value = float(yearly_totals.iloc[-1])

            if first_value != 0:
                percentage_change = (
                    (latest_value - first_value) / first_value
                ) * 100

                direction = (
                    "increased"
                    if percentage_change >= 0
                    else "decreased"
                )

                insights.append(
                    f"Recorded homelessness {direction} by "
                    f"{abs(percentage_change):.1f}% between "
                    f"{first_year} and {latest_year}."
                )

    if (
        race_count_column
        and race_category_column
        and race_count_column in race_dataframe.columns
        and race_category_column in race_dataframe.columns
        and not race_dataframe.empty
    ):
        race_totals = (
            race_dataframe.groupby(race_category_column)[race_count_column]
            .sum()
            .sort_values(ascending=False)
        )

        if not race_totals.empty:
            insights.append(
                f"The largest race or ethnicity category is "
                f"{race_totals.index[0]}."
            )

    if not insights:
        insights.append(
            "No analytical insights are available for the selected filters."
        )

    return insights[:4]


# ============================================================
# LOAD DATA
# ============================================================

age_df, race_df = load_database_tables(str(DATABASE_PATH))

data_quality_df = load_report(str(DATA_QUALITY_PATH))
pipeline_history_df = load_report(str(PIPELINE_HISTORY_PATH))


# ============================================================
# VALIDATE DATABASE
# ============================================================

if age_df.empty and race_df.empty:
    st.error(
        "The dashboard could not find usable data in "
        "`data/homelessness.db`."
    )

    st.info(
        "Run the ETL pipeline first:\n\n"
        "```bash\n"
        "python src/main.py\n"
        "```"
    )

    st.stop()


# ============================================================
# IDENTIFY AGE DATASET COLUMNS
# ============================================================

age_year_column = find_column(
    age_df,
    [
        "calendar_year",
        "year",
        "report_year",
    ],
)

age_location_column = find_column(
    age_df,
    [
        "location",
        "county",
        "coc_name",
        "continuum_of_care",
        "jurisdiction",
        "area",
    ],
)

age_category_column = find_column(
    age_df,
    [
        "age_group_public",
        "age_group",
        "age",
        "age_category",
        "category",
        "population_group",
    ],
)

age_count_column = find_column(
    age_df,
    [
        "experiencing_homelessness_cnt",
        "count",
        "homeless_count",
        "population",
        "total",
        "value",
        "number",
    ],
)


# ============================================================
# IDENTIFY RACE DATASET COLUMNS
# ============================================================

race_year_column = find_column(
    race_df,
    [
        "calendar_year",
        "year",
        "report_year",
    ],
)

race_location_column = find_column(
    race_df,
    [
        "location",
        "county",
        "coc_name",
        "continuum_of_care",
        "jurisdiction",
        "area",
    ],
)

race_category_column = find_column(
    race_df,
    [
        "race_ethnicity_public",
        "race_ethnicity",
        "race",
        "race_group",
        "ethnicity",
        "category",
    ],
)

race_count_column = find_column(
    race_df,
    [
        "experiencing_homelessness_cnt",
        "count",
        "homeless_count",
        "population",
        "total",
        "value",
        "number",
    ],
)


# ============================================================
# CLEAN NUMERIC DATA
# ============================================================

age_df = convert_numeric(age_df, age_year_column)
age_df = convert_numeric(age_df, age_count_column)

race_df = convert_numeric(race_df, race_year_column)
race_df = convert_numeric(race_df, race_count_column)

if age_count_column:
    age_df = age_df.dropna(subset=[age_count_column])

if race_count_column:
    race_df = race_df.dropna(subset=[race_count_column])


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-header">
        <h1>📊 California Homelessness Analytics Platform</h1>
        <p>
            Explore homelessness trends across California using an automated
            Python ETL pipeline, SQLite, data-quality validation, pipeline
            monitoring, geospatial mapping, and interactive analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("Dashboard Controls")

st.sidebar.caption(
    "Use the filters below to explore specific years and locations."
)

filtered_age_df = age_df.copy()
filtered_race_df = race_df.copy()


# ============================================================
# YEAR FILTER
# ============================================================

all_years: list[int] = []

if age_year_column:
    all_years.extend(
        age_df[age_year_column]
        .dropna()
        .astype(int)
        .tolist()
    )

if race_year_column:
    all_years.extend(
        race_df[race_year_column]
        .dropna()
        .astype(int)
        .tolist()
    )

available_years = sorted(set(all_years))
selected_years = available_years

if available_years:
    selected_years = st.sidebar.multiselect(
        "Select year",
        options=available_years,
        default=available_years,
    )

    if not selected_years:
        selected_years = available_years

    if age_year_column:
        filtered_age_df = filtered_age_df[
            filtered_age_df[age_year_column]
            .astype("Int64")
            .isin(selected_years)
        ]

    if race_year_column:
        filtered_race_df = filtered_race_df[
            filtered_race_df[race_year_column]
            .astype("Int64")
            .isin(selected_years)
        ]


# ============================================================
# LOCATION FILTER
# ============================================================

all_locations: list[str] = []

if age_location_column:
    all_locations.extend(
        age_df[age_location_column]
        .dropna()
        .astype(str)
        .tolist()
    )

if race_location_column:
    all_locations.extend(
        race_df[race_location_column]
        .dropna()
        .astype(str)
        .tolist()
    )

available_locations = sorted(set(all_locations))
selected_locations = available_locations

if available_locations:
    selected_locations = st.sidebar.multiselect(
        "Select location",
        options=available_locations,
        default=available_locations,
    )

    if not selected_locations:
        selected_locations = available_locations

    if age_location_column:
        filtered_age_df = filtered_age_df[
            filtered_age_df[age_location_column]
            .astype(str)
            .isin(selected_locations)
        ]

    if race_location_column:
        filtered_race_df = filtered_race_df[
            filtered_race_df[race_location_column]
            .astype(str)
            .isin(selected_locations)
        ]


st.sidebar.divider()

if st.sidebar.button(
    "Refresh dashboard data",
    use_container_width=True,
):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">Executive Summary</div>',
    unsafe_allow_html=True,
)

total_population = 0

if age_count_column and not filtered_age_df.empty:
    total_population = filtered_age_df[age_count_column].sum()
elif race_count_column and not filtered_race_df.empty:
    total_population = filtered_race_df[race_count_column].sum()


if age_location_column and not filtered_age_df.empty:
    total_locations = filtered_age_df[
        age_location_column
    ].nunique()
elif race_location_column and not filtered_race_df.empty:
    total_locations = filtered_race_df[
        race_location_column
    ].nunique()
else:
    total_locations = 0


selected_year_count = len(selected_years)


latest_pipeline_status = "Not Available"

if not pipeline_history_df.empty:
    pipeline_status_column = find_column(
        pipeline_history_df,
        [
            "status",
            "pipeline_status",
            "result",
        ],
    )

    if pipeline_status_column:
        latest_pipeline_status = str(
            pipeline_history_df.iloc[-1][pipeline_status_column]
        ).upper()


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

metric_col1.metric(
    "Total Population",
    format_number(total_population),
)

metric_col2.metric(
    "Locations",
    format_number(total_locations),
)

metric_col3.metric(
    "Years Selected",
    format_number(selected_year_count),
)

metric_col4.metric(
    "Latest ETL Status",
    latest_pipeline_status,
)


# ============================================================
# INTERACTIVE ANALYTICS TABS
# ============================================================

st.markdown(
    '<div class="section-title">Interactive Analytics</div>',
    unsafe_allow_html=True,
)

overview_tab, map_tab, age_tab, race_tab, data_tab = st.tabs(
    [
        "Overview",
        "California Map",
        "Age Analysis",
        "Race Analysis",
        "Data Explorer",
    ]
)


# ============================================================
# OVERVIEW TAB
# ============================================================

with overview_tab:

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Homelessness Trend")

        if (
            age_year_column
            and age_count_column
            and not filtered_age_df.empty
        ):
            yearly_totals = (
                filtered_age_df.groupby(
                    age_year_column,
                    as_index=False,
                )[age_count_column]
                .sum()
                .sort_values(age_year_column)
            )

            trend_chart = px.line(
                yearly_totals,
                x=age_year_column,
                y=age_count_column,
                markers=True,
                title="Total Population by Year",
                labels={
                    age_year_column: "Year",
                    age_count_column: "Population",
                },
            )

            trend_chart.update_layout(
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            trend_chart.update_yaxes(
                tickformat=",",
            )

            st.plotly_chart(
                trend_chart,
                use_container_width=True,
            )

        else:
            st.info(
                "Year and population columns were not found "
                "in the age dataset."
            )

    with chart_col2:
        st.subheader("Top Locations")

        if (
            age_location_column
            and age_count_column
            and not filtered_age_df.empty
        ):
            location_totals = (
                filtered_age_df.groupby(
                    age_location_column,
                    as_index=False,
                )[age_count_column]
                .sum()
                .nlargest(10, age_count_column)
                .sort_values(age_count_column)
            )

            location_chart = px.bar(
                location_totals,
                x=age_count_column,
                y=age_location_column,
                orientation="h",
                title="Top 10 Locations",
                labels={
                    age_location_column: "Location",
                    age_count_column: "Population",
                },
            )

            location_chart.update_layout(
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            location_chart.update_xaxes(
                tickformat=",",
            )

            st.plotly_chart(
                location_chart,
                use_container_width=True,
            )

        else:
            st.info(
                "Location and population columns were not found."
            )


# ============================================================
# CALIFORNIA MAP TAB
# ============================================================

with map_tab:

    st.subheader("Geographic Distribution")

    st.caption(
        "County estimates are derived from Continuum of Care locations. "
        "For multi-county CoCs, totals are divided equally across the "
        "counties listed in the CoC name."
    )

    if (
        age_location_column
        and age_count_column
        and not filtered_age_df.empty
    ):
        try:
            california_map = create_california_county_map(
                dataframe=filtered_age_df,
                location_column=age_location_column,
                count_column=age_count_column,
            )

            st.plotly_chart(
                california_map,
                use_container_width=True,
            )

        except Exception as error:
            st.error(
                f"California map could not be displayed: {error}"
            )

    else:
        st.info(
            "Location and population columns are required "
            "to display the California map."
        )


# ============================================================
# AGE ANALYSIS TAB
# ============================================================

with age_tab:

    st.subheader("Population by Age Category")

    if (
        age_category_column
        and age_count_column
        and not filtered_age_df.empty
    ):
        age_totals = (
            filtered_age_df.groupby(
                age_category_column,
                as_index=False,
            )[age_count_column]
            .sum()
            .sort_values(
                age_count_column,
                ascending=False,
            )
        )

        age_chart = px.bar(
            age_totals,
            x=age_category_column,
            y=age_count_column,
            title="Homelessness by Age Group",
            labels={
                age_category_column: "Age Group",
                age_count_column: "Population",
            },
            text_auto=",",
        )

        age_chart.update_layout(
            xaxis_tickangle=-35,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=80,
            ),
        )

        age_chart.update_yaxes(
            tickformat=",",
        )

        st.plotly_chart(
            age_chart,
            use_container_width=True,
        )

        st.dataframe(
            age_totals,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Age-category data is not available."
        )


# ============================================================
# RACE ANALYSIS TAB
# ============================================================

with race_tab:

    st.subheader("Population by Race or Ethnicity")

    if (
        race_category_column
        and race_count_column
        and not filtered_race_df.empty
    ):
        race_totals = (
            filtered_race_df.groupby(
                race_category_column,
                as_index=False,
            )[race_count_column]
            .sum()
            .sort_values(
                race_count_column,
                ascending=False,
            )
        )

        race_chart_col1, race_chart_col2 = st.columns(2)

        with race_chart_col1:
            race_bar_chart = px.bar(
                race_totals,
                x=race_category_column,
                y=race_count_column,
                title="Population by Race or Ethnicity",
                labels={
                    race_category_column: "Race or Ethnicity",
                    race_count_column: "Population",
                },
                text_auto=",",
            )

            race_bar_chart.update_layout(
                xaxis_tickangle=-35,
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=90,
                ),
            )

            race_bar_chart.update_yaxes(
                tickformat=",",
            )

            st.plotly_chart(
                race_bar_chart,
                use_container_width=True,
            )

        with race_chart_col2:
            race_pie_chart = px.pie(
                race_totals,
                names=race_category_column,
                values=race_count_column,
                title="Race and Ethnicity Distribution",
                hole=0.45,
            )

            race_pie_chart.update_traces(
                textposition="inside",
                textinfo="percent",
            )

            race_pie_chart.update_layout(
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
            )

            st.plotly_chart(
                race_pie_chart,
                use_container_width=True,
            )

        st.dataframe(
            race_totals,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Race-category data is not available."
        )


# ============================================================
# DATA EXPLORER TAB
# ============================================================

with data_tab:

    dataset_selection = st.radio(
        "Choose a dataset",
        options=[
            "Homelessness by Age",
            "Homelessness by Race",
        ],
        horizontal=True,
    )

    if dataset_selection == "Homelessness by Age":
        st.dataframe(
            filtered_age_df,
            use_container_width=True,
            hide_index=True,
        )

        create_download_button(
            label="Download filtered age data",
            dataframe=filtered_age_df,
            filename="filtered_homelessness_by_age.csv",
            key="download_age_data",
        )

    else:
        st.dataframe(
            filtered_race_df,
            use_container_width=True,
            hide_index=True,
        )

        create_download_button(
            label="Download filtered race data",
            dataframe=filtered_race_df,
            filename="filtered_homelessness_by_race.csv",
            key="download_race_data",
        )


# ============================================================
# AUTOMATIC INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">Automatic Insights</div>',
    unsafe_allow_html=True,
)

generated_insights = build_insights(
    age_dataframe=filtered_age_df,
    race_dataframe=filtered_race_df,
    age_year_column=age_year_column,
    age_category_column=age_category_column,
    age_location_column=age_location_column,
    age_count_column=age_count_column,
    race_category_column=race_category_column,
    race_count_column=race_count_column,
)

for insight in generated_insights:
    st.markdown(
        f"""
        <div class="insight-card">
            💡 {insight}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PIPELINE MONITORING
# ============================================================

st.markdown(
    '<div class="section-title">Pipeline Monitoring</div>',
    unsafe_allow_html=True,
)

monitoring_col1, monitoring_col2 = st.columns([1, 2])

with monitoring_col1:

    if pipeline_history_df.empty:
        st.warning(
            "Pipeline run history is not available."
        )

    else:
        status_column = find_column(
            pipeline_history_df,
            [
                "status",
                "pipeline_status",
                "result",
            ],
        )

        runtime_column = find_column(
            pipeline_history_df,
            [
                "duration_seconds",
                "runtime_seconds",
                "runtime",
                "execution_time",
            ],
        )

        timestamp_column = find_column(
            pipeline_history_df,
            [
                "run_time",
                "timestamp",
                "run_timestamp",
                "date",
            ],
        )

        latest_run = pipeline_history_df.iloc[-1]

        latest_status = (
            str(latest_run[status_column]).upper()
            if status_column
            else "UNKNOWN"
        )

        if latest_status == "PASS":
            st.markdown(
                """
                <div class="status-pass">
                    ✅ Latest Pipeline Run: PASS
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="status-fail">
                    ⚠ Latest Pipeline Run: {latest_status}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if timestamp_column:
            st.metric(
                "Latest Run",
                str(latest_run[timestamp_column]),
            )

        if runtime_column:
            try:
                runtime_value = float(
                    latest_run[runtime_column]
                )

                st.metric(
                    "Runtime",
                    f"{runtime_value:.2f} seconds",
                )

            except (TypeError, ValueError):
                st.metric(
                    "Runtime",
                    str(latest_run[runtime_column]),
                )


with monitoring_col2:

    if not pipeline_history_df.empty:
        st.subheader("Pipeline Run History")

        st.dataframe(
            pipeline_history_df.tail(10).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

        create_download_button(
            label="Download pipeline history",
            dataframe=pipeline_history_df,
            filename="pipeline_run_history.csv",
            key="download_pipeline_history",
        )


# ============================================================
# DATA QUALITY
# ============================================================

st.markdown(
    '<div class="section-title">Data Quality</div>',
    unsafe_allow_html=True,
)

if data_quality_df.empty:
    st.warning(
        "The data-quality report is not available."
    )

else:
    quality_status_column = find_column(
        data_quality_df,
        [
            "status",
            "overall_status",
            "result",
        ],
    )

    quality_col1, quality_col2, quality_col3 = st.columns(3)

    total_quality_checks = len(data_quality_df)

    passing_checks = 0

    if quality_status_column:
        passing_checks = (
            data_quality_df[quality_status_column]
            .astype(str)
            .str.upper()
            .eq("PASS")
            .sum()
        )

    quality_score = 0

    if total_quality_checks > 0:
        quality_score = (
            passing_checks / total_quality_checks
        ) * 100

    quality_col1.metric(
        "Quality Checks",
        format_number(total_quality_checks),
    )

    quality_col2.metric(
        "Passing Checks",
        format_number(passing_checks),
    )

    quality_col3.metric(
        "Quality Score",
        f"{quality_score:.1f}%",
    )

    st.dataframe(
        data_quality_df,
        use_container_width=True,
        hide_index=True,
    )

    create_download_button(
        label="Download data-quality report",
        dataframe=data_quality_df,
        filename="data_quality_report.csv",
        key="download_quality_report",
    )


# ============================================================
# ABOUT SECTION
# ============================================================

with st.expander("About this project"):

    st.markdown(
        """
        This portfolio project demonstrates an end-to-end data engineering
        and analytics workflow.

        **Technology stack**

        - Python
        - Pandas
        - SQLite
        - SQL
        - Plotly
        - Streamlit
        - Pytest
        - YAML configuration
        - GitHub Actions
        - Docker

        **Pipeline architecture**

        `Raw CSV → Extract → Transform → Validate → SQLite → SQL Analytics
        → Reports → Dashboard → Monitoring`
        """
    )


st.divider()

st.caption(
    "California Homelessness Analytics Platform | "
    "Python Data Engineering Portfolio Project"
)