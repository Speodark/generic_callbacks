import pandas as pd
from dash import dcc
import uuid

def date_picker_range(df, column_name, id=None):
    id = str(uuid.uuid4()) if not id else id
    min_date, max_date = pd.to_datetime(
        df[column_name].min()), pd.to_datetime(df[column_name].max())
    return dcc.DatePickerRange(
        # ID to be used for callback
        id={'type': 'date_picker_range', 'column_name':column_name, 'id': id},
        calendar_orientation='horizontal',  # vertical or horizontal
        day_size=39,  # size of calendar image. Default is 39
        # end_date_placeholder_text="Return",  # text that appears when no end date chosen
        with_portal=False,  # if True calendar will open in a full screen overlay portal
        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
        reopen_calendar_on_clear=True,
        is_RTL=False,  # True or False for direction of calendar
        clearable=False,  # whether or not the user can clear the dropdown
        number_of_months_shown=2,  # number of months shown when calendar is open
        min_date_allowed=min_date,  # minimum date allowed on the DatePickerRange component
        max_date_allowed=max_date,  # maximum date allowed on the DatePickerRange component
        # the month initially presented when the user opens the calendar
        initial_visible_month=max_date,
        start_date=min_date.date(),
        end_date=max_date.date(),
        # how selected dates are displayed in the DatePickerRange component.
        display_format='MMM Do, YY',
        # how calendar headers are displayed when the calendar is opened.
        month_format='MMMM, YYYY',
        minimum_nights=2,  # minimum number of days between start and end date
        # persistence=True,
        # persisted_props=['start_date', 'end_date'],
        # persistence_type='session',  # session, local, or memory. Default is 'local'
        # # singledate or bothdates. Determines when callback is triggered
        updatemode='singledate',
        stay_open_on_select=True,
        className='header__date-picker-range'
    )
