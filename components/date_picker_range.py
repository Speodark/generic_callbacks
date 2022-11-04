import pandas as pd
from dash import dcc, Output, Input, ALL
import uuid
import ast
from filter_manager import filter_manager

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


######################################## For filter manager

# Goes through all the date picker range and filter the dataframe by each of them except the active_id one.
@filter_manager.register_filter_functions('date_picker_range')
def filter_by_date_picker_range(df, data, active_id=None):
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)["column_name"]
            start_date = data[filter_id]["start_date"]
            end_date = data[filter_id]["end_date"]
            df = df[(df[column_name] >= start_date) & (df[column_name] <= end_date)]

    return df


# Create date_picker_range outputs
# IMPORTANT NOTE FOR LATER
# this component require 5 outputs, when we build the manager and add the outputs by decorator
# we need to make sure we return the values the same order we pass the outputs else it wont work.
@filter_manager.register_component_generator('date_picker_range')
def create_dpr_output(dfs, components_data):
    """
    In the dfs variable we get
    {component_id:df}
    the function creates the components for each component using the component df
    In the data variable we get
    {component_id: {'start_date':value, 'end_date':'value'}}
    """
    start_dates = []
    end_dates = []
    min_date_alloweds = []
    max_date_alloweds = []
    initial_visible_months = []
    for dpr_id in dfs.keys():
        column_name = ast.literal_eval(dpr_id)["column_name"]

        # get the minimum and maximum dates, we have to convert them from numpy array to pandas datetime.
        min_date, max_date = (
            pd.to_datetime(dfs[dpr_id][column_name].min()),
            pd.to_datetime(dfs[dpr_id][column_name].max()),
        )
        # Check if the min date is lower then current date same with max
        start_date, end_date = (
            pd.to_datetime(components_data[dpr_id]["start_date"]),
            pd.to_datetime(components_data[dpr_id]["end_date"]),
        )
        start_date = start_date if start_date >= min_date else min_date
        end_date = end_date if end_date <= max_date else max_date
        # Append the variables
        start_dates.append(start_date)
        end_dates.append(end_date)
        min_date_alloweds.append(min_date)
        max_date_alloweds.append(max_date)
        initial_visible_months.append(end_date)
    return (
        start_dates,
        end_dates,
        min_date_alloweds,
        max_date_alloweds,
        initial_visible_months,
    )

filter_manager.register_inputs_outputs(
    Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
    Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
    Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
    Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
)