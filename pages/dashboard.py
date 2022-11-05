import vaex
from dash import html, dcc
from layout import header, sub_header
from components import (
    card,
    horizontal_bar_chart,
    stacked_bar_chart,
    date_picker_range,
    binary_filter,
    kpi,
    range_slider
)
import uuid

df = vaex.open("assets/data/data.hdf5")


def dashboard():
    return html.Div(
        className="dashboard",
        children=[
            kpi(
                text="Animal Count",
                value=len(df),
                className="sub-header__animal-count",
                kpi_name="animal_count",
            ),
            kpi(
                text="Adopted",
                value=len(df[df.outcome_type == "Adoption"]),
                className="sub-header__adopted",
                kpi_name="adopted",
            ),
            date_picker_range(df, column_name="datetime"),
            date_picker_range(df, column_name="date_of_birth"),
            card(
                header="Animal Type",
                children=horizontal_bar_chart(
                    categories="animal_type", value_by="count", df=df
                ),
                className="dashboard__animal-type center_items_vertical",
            ),
            card(
                header="Outcome",
                children=horizontal_bar_chart(
                    categories="outcome_type", value_by="count", df=df
                ),
                className="dashboard__outcome center_items_vertical",
            ),
            binary_filter(
                column_name="sex",
                categories=["Male", "Female"],
                colors=["pink", "#2B80FF"],
                className="sub-header__gender",
            ),
            binary_filter(
                column_name="castrated",
                categories=["castrated", "not castrated"],
                colors=["green", "red"],
                className="sub-header__castrated",
            ),
            card(
                header="age upon outcome",
                children=range_slider('age_upon_outcome', df)
            ),
            card(
                header="Amount of outcome by Type and Date",
                children=stacked_bar_chart(
                    x_axis="datetime", y_axis="count", category="outcome_type", df=df
                ),
                className="dashboard__overview--outcome-time center_items_vertical",
            ),
        ],
    )
