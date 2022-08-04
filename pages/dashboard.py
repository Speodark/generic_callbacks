import vaex
from dash import html, dcc
from layout import (
    header,
    sub_header
)
from components import (
    card,
    horizontal_bar_chart,
    stacked_bar_chart,
    date_picker_range,
    binary_filter
)
from pages.callbacks import *


# The overview tab
def overview_tab(df):
    return html.Div(
        children=[
            # Outcome graph
            card(
                header='Outcome',
                children=horizontal_bar_chart(
                    category_name='outcome_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__overview--outcome center_items_vertical"
            ),
            # Animal Type graph
            card(
                header='Animal Type',
                children=horizontal_bar_chart(
                    category_name='animal_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__overview--animal-type center_items_vertical"
            ),
            # Animal Type graph
            card(
                header='Amount of outcome by Type and Date',
                children=stacked_bar_chart(
                    x_axis='datetime',
                    y_axis='count',
                    category='outcome_type',
                    df=df
                ),
                className="dashboard__overview--outcome-time center_items_vertical"
            ),
            # Age slider
            html.Div(
                children=[
                    html.Span("Age upon outcome Range"),
                    dcc.RangeSlider(
                        min=int(df.age_upon_outcome.min()),
                        max=int(df.age_upon_outcome.max()),
                        step=1,
                        value=[int(df.age_upon_outcome.min()),
                               int(df.age_upon_outcome.max())],
                        id={'type': 'range_slider', 'id': 'age_upon_outcome'},
                        className="dashboard__overview--age-range__slider"
                    )
                ],
                className="dashboard__overview--age-range"
            )

        ],
        className='dashboard__overview'
    )


def dashboard():
    df = vaex.open('assets/data/data.hdf5')
    return html.Div(
        className='dashboard',
        children=[
            card(
                children=date_picker_range(df, 'datetime'),
                className='dashboard__datetime'
            ),
            card(
                children=date_picker_range(df, 'date_of_birth'),
                className='dashboard__date_of_birth'
            ),
            card(
                header='Animal Type',
                children=horizontal_bar_chart(
                    category_name='animal_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__animal-type center_items_vertical"
            ),
            card(
                header='Outcome',
                children=horizontal_bar_chart(
                    category_name='outcome_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__outcome center_items_vertical"
            ),
            binary_filter(
                id='sex',
                categories=['Male', 'Female'],
                colors=['pink', '#2B80FF'],
                className='sub-header__gender'
            ),
            binary_filter(
                id='castrated',
                categories=['castrated', 'not castrated'],
                colors=['green', 'red'],
                className='sub-header__castrated'
            )
        ]
    )
