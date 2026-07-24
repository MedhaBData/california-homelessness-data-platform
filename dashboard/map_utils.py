from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GEOJSON_PATH = (
    PROJECT_ROOT / "data" / "geo" / "california_counties.geojson"
)


# City-based CoCs that belong to Los Angeles County.
CITY_TO_COUNTY = {
    "glendale": "Los Angeles",
    "long beach": "Los Angeles",
    "pasadena": "Los Angeles",
}


def load_california_geojson(
    geojson_path: Path = GEOJSON_PATH,
) -> dict[str, Any]:
    """
    Load the California county GeoJSON file.
    """
    if not geojson_path.exists():
        raise FileNotFoundError(
            f"GeoJSON file not found: {geojson_path}"
        )

    with geojson_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def detect_geojson_county_property(
    geojson_data: dict[str, Any],
) -> str:
    """
    Detect which GeoJSON property contains the county name.
    """
    features = geojson_data.get("features", [])

    if not features:
        raise ValueError("The GeoJSON file contains no features.")

    properties = features[0].get("properties", {})

    candidate_properties = [
        "name",
        "NAME",
        "county",
        "COUNTY",
        "County",
        "namelsad",
        "NAMELSAD",
    ]

    for candidate in candidate_properties:
        if candidate in properties:
            return candidate

    raise ValueError(
        "Could not identify the county-name property in the GeoJSON."
    )


def normalize_county_name(value: str) -> str:
    """
    Normalize county names for matching.
    """
    county_name = str(value).strip()

    county_name = re.sub(
        r"\s+County$",
        "",
        county_name,
        flags=re.IGNORECASE,
    )

    return county_name.strip()


def extract_counties_from_location(
    location: str,
) -> list[str]:
    """
    Convert a CoC location label into one or more California counties.

    Examples:
        Alameda County CoC -> ["Alameda"]
        Fresno, Madera Counties CoC -> ["Fresno", "Madera"]
        Glendale CoC (Los Angeles County) -> ["Los Angeles"]
    """
    if pd.isna(location):
        return []

    text = str(location).strip()

    if not text:
        return []

    if text.lower() == "california":
        return []

    parenthetical_match = re.search(
        r"\((.*?)\)",
        text,
    )

    if parenthetical_match:
        parenthetical_text = parenthetical_match.group(1)
        parenthetical_text = re.sub(
            r"\s+County$",
            "",
            parenthetical_text,
            flags=re.IGNORECASE,
        )

        return [
            normalize_county_name(parenthetical_text)
        ]

    city_key = (
        text.lower()
        .replace(" coc", "")
        .strip()
    )

    if city_key in CITY_TO_COUNTY:
        return [CITY_TO_COUNTY[city_key]]

    cleaned_text = re.sub(
        r"\s+CoC.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s+Counties$",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s+County$",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    county_names = [
        normalize_county_name(part)
        for part in cleaned_text.split(",")
        if part.strip()
    ]

    return county_names


def allocate_coc_totals_to_counties(
    dataframe: pd.DataFrame,
    location_column: str,
    count_column: str,
) -> pd.DataFrame:
    """
    Allocate each CoC total across the counties named in that CoC.

    For multi-county CoCs, the total is divided equally among counties.
    This is an approximation for visualization purposes.
    """
    required_columns = {
        location_column,
        count_column,
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    working_df = dataframe[
        [
            location_column,
            count_column,
        ]
    ].copy()

    working_df[count_column] = pd.to_numeric(
        working_df[count_column],
        errors="coerce",
    )

    working_df = working_df.dropna(
        subset=[
            location_column,
            count_column,
        ]
    )

    county_records: list[dict[str, Any]] = []

    for _, row in working_df.iterrows():
        location = row[location_column]
        count = float(row[count_column])

        counties = extract_counties_from_location(location)

        if not counties:
            continue

        allocated_count = count / len(counties)

        for county in counties:
            county_records.append(
                {
                    "county": county,
                    "homelessness_count": allocated_count,
                    "source_location": location,
                }
            )

    if not county_records:
        return pd.DataFrame(
            columns=[
                "county",
                "homelessness_count",
            ]
        )

    county_df = pd.DataFrame(county_records)

    county_totals = (
        county_df.groupby(
            "county",
            as_index=False,
        )["homelessness_count"]
        .sum()
        .sort_values(
            "homelessness_count",
            ascending=False,
        )
    )

    county_totals["homelessness_count"] = (
        county_totals["homelessness_count"]
        .round()
        .astype(int)
    )

    return county_totals


def create_california_county_map(
    dataframe: pd.DataFrame,
    location_column: str,
    count_column: str,
) -> go.Figure:
    """
    Create an interactive Plotly choropleth map of California counties.
    """
    geojson_data = load_california_geojson()
    county_property = detect_geojson_county_property(
        geojson_data
    )

    county_totals = allocate_coc_totals_to_counties(
        dataframe=dataframe,
        location_column=location_column,
        count_column=count_column,
    )

    if county_totals.empty:
        figure = go.Figure()

        figure.add_annotation(
            text="No county-level data is available for the selected filters.",
            showarrow=False,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
        )

        figure.update_layout(
            height=650,
            margin=dict(
                l=0,
                r=0,
                t=30,
                b=0,
            ),
        )

        return figure

    for feature in geojson_data["features"]:
        properties = feature.get("properties", {})

        if county_property in properties:
            properties[county_property] = normalize_county_name(
                properties[county_property]
            )

    figure = px.choropleth(
        county_totals,
        geojson=geojson_data,
        locations="county",
        featureidkey=f"properties.{county_property}",
        color="homelessness_count",
        hover_name="county",
        hover_data={
            "homelessness_count": ":,",
            "county": False,
        },
        labels={
            "homelessness_count": "Estimated Population",
        },
        title="Estimated Homelessness by California County",
    )

    figure.update_geos(
        fitbounds="locations",
        visible=False,
    )

    figure.update_layout(
        height=700,
        margin=dict(
            l=0,
            r=0,
            t=60,
            b=0,
        ),
        coloraxis_colorbar=dict(
            title="Population",
            tickformat=",",
        ),
    )

    return figure
