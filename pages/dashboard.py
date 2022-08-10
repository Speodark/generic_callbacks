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
    binary_filter,
    kpi
)
from pages.callbacks import *
import uuid


def dashboard():
    df = vaex.open('assets/data/data.hdf5')
    return html.Div(
        className='dashboard',
        children=[
            kpi(
                text='Animal Count', 
                value=len(df),
                className='sub-header__animal-count',
                kpi_name = 'animal_count'
            ),
            kpi(
                text='Adopted', 
                value=len(df[df.outcome_type == 'Adoption']),
                className='sub-header__adopted',
                kpi_name = 'adopted'
            ),
            date_picker_range(df, column_name='datetime'),
            date_picker_range(df, column_name='date_of_birth'),
            card(
                header='Animal Type',
                children=horizontal_bar_chart(
                    categories='animal_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__animal-type center_items_vertical"
            ),
            card(
                header='Outcome',
                children=horizontal_bar_chart(
                    categories='outcome_type',
                    value_by='count',
                    df=df
                ),
                className="dashboard__outcome center_items_vertical"
            ),
            binary_filter(
                column_name='sex',
                categories=['Male', 'Female'],
                colors=['pink', '#2B80FF'],
                className='sub-header__gender'
            ),
            binary_filter(
                column_name='castrated',
                categories=['castrated', 'not castrated'],
                colors=['green', 'red'],
                className='sub-header__castrated'
            ),
            card(
                header="age upon outcome",
                children=dcc.RangeSlider(
                    min=int(df.age_upon_outcome.min()),
                    max=int(df.age_upon_outcome.max()),
                    step=1,
                    value=[int(df.age_upon_outcome.min()),int(df.age_upon_outcome.max())],
                    id={'type':'range_slider','id':str(uuid.uuid4()), 'column_name':'age_upon_outcome'}, 
                )
            )
        ]
    )
