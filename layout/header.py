from dash import html, dcc
import pandas as pd

def header(df, className = ''):
    min_date, max_date = pd.to_datetime(df['datetime'].min()), pd.to_datetime(df['datetime'].max())
    return html.Div(
        className = 'header ' + className,
        children=[
            dcc.DatePickerRange(
                id='date-range',  # ID to be used for callback
                calendar_orientation='horizontal',  # vertical or horizontal
                day_size=39,  # size of calendar image. Default is 39
                end_date_placeholder_text="Return",  # text that appears when no end date chosen
                with_portal=False,  # if True calendar will open in a full screen overlay portal
                first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                reopen_calendar_on_clear=True,
                is_RTL=False,  # True or False for direction of calendar
                clearable=False,  # whether or not the user can clear the dropdown
                number_of_months_shown=2,  # number of months shown when calendar is open
                min_date_allowed=min_date,  # minimum date allowed on the DatePickerRange component
                max_date_allowed=max_date,  # maximum date allowed on the DatePickerRange component
                initial_visible_month=max_date,  # the month initially presented when the user opens the calendar
                start_date=min_date.date(),
                end_date=max_date.date(),
                display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                minimum_nights=2,  # minimum number of days between start and end date
                persistence=True,
                persisted_props=['start_date'],
                persistence_type='session',  # session, local, or memory. Default is 'local'
                updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
                stay_open_on_select = True,
                className='header__date-picker-range'
            ),
            html.P(children='Animal Shelter', className='header__title'),
            html.Div(
                children=html.Button(
                    children=[
                        html.Span('Export'),
                        html.Span(className='arrow arrow__down header__export--arrow')
                    ],
                    className='header__export--btn',
                    n_clicks=0,
                    id = 'export'
                ),
                className='header__export'
            )
            
        ]
    )