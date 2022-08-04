import vaex
import ast
import pandas as pd
import dash
from dash import Input, Output, ALL, State, MATCH, ctx
from dash.exceptions import PreventUpdate
from components import (
    horizontal_bar_chart_figure,
    stacked_bar_chart_figure
)

df = vaex.open('assets/data/data.hdf5')


# filtering by the binary filters
def filter_by_binary_filters(filtered_df, binary_filters):
    # going through all the binary filters ids
    for key, value in binary_filters.items():
        # checking if the binary filter been activated
        if value['children']:
            # filtering the dataframe by the binary filter
            filter_id = ast.literal_eval(key)['id']
            filtered_df = filtered_df[filtered_df[filter_id]
                                      == value['children']]
    # Returning the df
    return filtered_df


# filtering by the bar charts selected data
def filter_by_bar_chart_data(ids, bar_charts_data, filtered_df):
    # going through all the bar charts ids
    for index, bar_chart_id in enumerate(ids):
        # checking if there are selected data
        if bar_charts_data[index] and bar_charts_data[index]['points']:
            categories = []
            # going through each bar in the selected bar charts to get the choosen categories
            for bar in bar_charts_data[index]['points']:
                categories.append(bar['y'])
            # filtering the dataframe by the bar charts
            filtered_df = filtered_df[filtered_df[bar_chart_id].isin(
                categories)]
    return filtered_df


# filtering by the range slider value
def filter_by_range_slider(ids, range_sliders_data, filtered_df):
    # going through all the range sliders ids
    for index, range_slider_id in enumerate(ids):
        # checking if the value is not none
        if range_sliders_data[index][0] is not None and range_sliders_data[index][1] is not None:
            # filtering the dataframe by the range slider value
            filtered_df = filtered_df[
                (filtered_df[range_slider_id] >= range_sliders_data[index][0]) &
                (filtered_df[range_slider_id] <= range_sliders_data[index][1])
            ]
    return filtered_df


def filter_by_date_picker_range(df, start_date, end_date):
    print("hello", start_date, end_date)


@dash.callback(
    Output({'type': 'date_picker_range', 'id': ALL}, 'start_date'),
    Output({'type': 'date_picker_range', 'id': ALL}, 'end_date'),
    Output({'type': 'date_picker_range', 'id': ALL}, 'min_date_allowed'),
    Output({'type': 'date_picker_range', 'id': ALL}, 'max_date_allowed'),
    Input({'type': 'date_picker_range', 'id': ALL}, 'start_date'),
    Input({'type': 'date_picker_range', 'id': ALL}, 'end_date'),
    Input({'type': 'binary_filter', 'id': ALL, 'sub_type': 'value'}, 'children')
)
def dashboard_update(*args):
    # for each type we have a filtering function
    functions_type_dict = {
        'date_picker_range': filter_by_date_picker_range,
        'binary_filter': filter_by_binary_filters
    }
    # gets the dictionary of dictionaries of all the Inputs type and values
    type_dict = {key: {} for key in functions_type_dict.keys()}
    for callback_input_index, callback_input in enumerate(ctx.inputs_list):
        for input_id_index, input_id in enumerate(callback_input):
            try:
                type_dict[input_id['id']['type']
                          ][str(input_id['id'])][input_id['property']] = args[callback_input_index][input_id_index]
            except:
                type_dict[input_id['id']['type']][str(input_id['id'])] = {
                    input_id['property']: args[callback_input_index][input_id_index]
                }
    # get all unique output types
    output_type_list = []
    for output in ctx.outputs_list:
        for output_id in output:
            if output_id['id']['type'] not in output_type_list:
                output_type_list.append(output_id['id']['type'])
            break

    # create
    input_type_list = list(type_dict.keys())
    output_without_input_type = list(
        set(input_type_list) - set(output_type_list))
    ordred_type_list = output_without_input_type.copy()
    ordred_type_list.extend(output_type_list)

    # for each input type we go over all input types again and filter by them except for the current input_type.
    filtered_df = df
    for input_type in ordred_type_list:
        if input_type in output_without_input_type:
            filtered_df = functions_type_dict[input_type](
                filtered_df, type_dict[input_type])

    return args, args

# @dash.callback(
#     Output('date-range', 'start_date'),
#     Output('date-range', 'end_date'),
#     Output('date-range', 'min_date_allowed'),
#     Output('date-range', 'max_date_allowed'),
#     Output('date-range', 'initial_visible_month'),
#     Input({'type':'binary_filter','id':ALL, 'sub_type':'value'}, 'children'),
#     Input({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
#     Input({'type':'range_slider','id':ALL}, 'value'),
#     State('date-range', 'start_date'),
#     State('date-range', 'end_date'),
#     prevent_initial_call=True
# )
# def update_date_picker(binary_filters, bar_charts_data, range_sliders_data, start_date, end_date):
#     # making a copy of the original dataframe
#     filtered_df = df
#     # getting a list of ids of all the binary filters
#     binary_filters_ids = [id['id']['id'] for id in ctx.inputs_list[0]]
#     # filtering by the binary filters
#     filtered_df = filter_by_binary_filters(binary_filters_ids, binary_filters, filtered_df)
#     # getting a list of ids of all the bar charts
#     bar_Charts_ids = [id['id']['id'] for id in ctx.inputs_list[1]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_bar_chart_data(bar_Charts_ids, bar_charts_data, filtered_df)
#     # getting a list of ids of all the range sliders
#     range_sliders_ids = [id['id']['id'] for id in ctx.inputs_list[2]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_range_slider(range_sliders_ids, range_sliders_data, filtered_df)
#     # get the minimum and maximum dates, we have to convert them from numpy array to pandas datetime.
#     min_date, max_date = pd.to_datetime(filtered_df['datetime'].min()), pd.to_datetime(filtered_df['datetime'].max())
#     # Check if the min date is lower then current date same with max
#     start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
#     start_date = start_date if start_date <= min_date else min_date
#     end_date = end_date if end_date >= max_date else max_date
#     # Return the dates
#     return start_date, end_date, min_date, max_date, max_date
# @dash.callback(
#     Output({'type':'kpi','id':ALL}, 'children'),
#     Input({'type':'binary_filter','id':ALL, 'sub_type':'value'}, 'children'),
#     Input({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
#     Input({'type':'range_slider','id':ALL}, 'value'),
#     Input('date-range','start_date'),
#     Input('date-range','end_date'),
#     prevent_initial_call=True
# )
# def update_kpi(binary_filters, bar_charts_data, range_sliders_data, date_start, date_end):
#     # making a copy of the original dataframe
#     filtered_df = df
#     # getting a list of ids of all the binary filters
#     binary_filters_ids = [id['id']['id'] for id in ctx.inputs_list[0]]
#     # filtering by the binary filters
#     filtered_df = filter_by_binary_filters(binary_filters_ids, binary_filters, filtered_df)
#     # getting a list of ids of all the bar charts
#     bar_Charts_ids = [id['id']['id'] for id in ctx.inputs_list[1]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_bar_chart_data(bar_Charts_ids, bar_charts_data, filtered_df)
#     # getting a list of ids of all the range sliders
#     range_sliders_ids = [id['id']['id'] for id in ctx.inputs_list[2]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_range_slider(range_sliders_ids, range_sliders_data, filtered_df)
#     # Filtering the data by the start and end date from date picker
#     filtered_df = filtered_df[
#         (filtered_df['datetime']>=date_start) &
#         (filtered_df['datetime']<=date_end)
#     ]
#     # get the kpi data to return for each kpi.
#     kpi_ids = [id['id']['id'] for id in ctx.outputs_list]
#     kpi_values = []
#     # going through all the kpi ids
#     for kpi_id in kpi_ids:
#         if kpi_id == 'animal_count':
#             kpi_values.append(len(filtered_df))
#         elif kpi_id == 'adopted':
#             kpi_values.append(len(filtered_df[filtered_df.outcome_type == 'Adoption']))
#     # Return the kpi values
#     return kpi_values
# @dash.callback(
#     Output({'type':'range_slider','id':ALL}, 'min'),
#     Output({'type':'range_slider','id':ALL}, 'max'),
#     Input({'type':'binary_filter','id':ALL, 'sub_type':'value'}, 'children'),
#     Input({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
#     Input('date-range','start_date'),
#     Input('date-range','end_date'),
#     prevent_initial_call=True
# )
# def update_range_sliders(binary_filters, bar_charts_data, date_start, date_end):
#     # making a copy of the original dataframe
#     filtered_df = df
#     # getting a list of ids of all the binary filters
#     binary_filters_ids = [id['id']['id'] for id in ctx.inputs_list[0]]
#     # filtering by the binary filters
#     filtered_df = filter_by_binary_filters(binary_filters_ids, binary_filters, filtered_df)
#     # getting a list of ids of all the bar charts
#     bar_Charts_ids = [id['id']['id'] for id in ctx.inputs_list[1]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_bar_chart_data(bar_Charts_ids, bar_charts_data, filtered_df)
#     # Filtering the data by the start and end date from date picker
#     filtered_df = filtered_df[
#         (filtered_df['datetime']>=date_start) &
#         (filtered_df['datetime']<=date_end)
#     ]
#     range_sliders_ids = [id['id']['id'] for id in ctx.outputs_list[0]]
#     range_sliders_minimums = []
#     range_sliders_maximums = []
#     for range_slider in range_sliders_ids:
#         range_sliders_minimums.append(int(filtered_df[range_slider].min()))
#         range_sliders_maximums.append(int(filtered_df[range_slider].max()))
#     # Return the kpi values
#     return range_sliders_minimums, range_sliders_maximums
# @dash.callback(
#     Output({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL}, 'figure'),
#     Input({'type':'binary_filter','id':ALL, 'sub_type':'value'}, 'children'),
#     Input({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
#     Input({'type':'range_slider','id':ALL}, 'value'),
#     Input('date-range','start_date'),
#     Input('date-range','end_date'),
#     prevent_initial_call=True
# )
# def update_bar_charts(binary_filters, bar_charts_data, range_sliders_data, date_start, date_end):
#     # making a copy of the original dataframe
#     filtered_df = df
#     # getting a list of ids of all the binary filters
#     binary_filters_ids = [id['id']['id'] for id in ctx.inputs_list[0]]
#     # filtering by the binary filters
#     filtered_df = filter_by_binary_filters(binary_filters_ids, binary_filters, filtered_df)
#     # getting a list of ids of all the range sliders
#     range_sliders_ids = [id['id']['id'] for id in ctx.inputs_list[2]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_range_slider(range_sliders_ids, range_sliders_data, filtered_df)
#     # Filtering the data by the start and end date from date picker
#     filtered_df = filtered_df[
#         (filtered_df['datetime']>=date_start) &
#         (filtered_df['datetime']<=date_end)
#     ]
#     # For future big callback refrence
#     # if isinstance(ctx.triggered_id,dict) and ctx.triggered_id['type'] == 'bar_chart':
#     # getting a list of ids of all the bar charts
#     bar_charts_ids = [id['id'] for id in ctx.inputs_list[1]]
#     bar_charts_filtered_df = []
#     # filtering by the bar charts selected data
#     for index in range(len(bar_charts_ids)):
#         # Get all the bar charts data and id excluding the current filtering graph
#         filter_data = bar_charts_data[:index] + bar_charts_data[index+1:]
#         filter_ids = bar_charts_ids[:index] + bar_charts_ids[index+1:]
#         # Get the categories from the id
#         filter_ids = [filter_id['id'] for filter_id in filter_ids]
#         bar_charts_filtered_df.append(filter_by_bar_chart_data(filter_ids, filter_data, filtered_df))
#     bar_charts = []
#     for index, (dataframe, chart_id) in enumerate(zip(bar_charts_filtered_df, bar_charts_ids)):
#         # Getting the dataframe ready for the chart
#         dataframe = dataframe.groupby([chart_id['id']],agg=chart_id['agg'])
#         dataframe = dataframe.sort(chart_id['value_by']).to_pandas_df().reset_index(drop=True)
#         # Getting selected points if there are any
#         selected_points = None
#         if bar_charts_data[index] and bar_charts_data[index]['points']:
#             selected = [point_index['y'] for point_index in bar_charts_data[index]['points']]
#             selected_points = dataframe[dataframe[chart_id['id']].isin(selected)].index.values
#         # creating the chart and appending it to the charts list
#         bar_charts.append(
#             horizontal_bar_chart_figure(
#                 categories=dataframe[chart_id['id']],
#                 values=dataframe[chart_id['value_by']],
#                 selected_points=selected_points
#             )
#         )
#     return bar_charts
# @dash.callback(
#     Output({'type':'stacked_bar_chart','id':ALL, 'x_axis':ALL, 'y_axis':ALL, 'agg':ALL}, 'figure'),
#     Input({'type':'binary_filter','id':ALL, 'sub_type':'value'}, 'children'),
#     Input({'type':'bar_chart','id':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
#     Input({'type':'range_slider','id':ALL}, 'value'),
#     Input('date-range','start_date'),
#     Input('date-range','end_date'),
#     prevent_initial_call=True
# )
# def update_bar_charts(binary_filters, bar_charts_data, range_sliders_data, date_start, date_end):
#     # making a copy of the original dataframe
#     filtered_df = df
#     # getting a list of ids of all the binary filters
#     binary_filters_ids = [id['id']['id'] for id in ctx.inputs_list[0]]
#     # filtering by the binary filters
#     filtered_df = filter_by_binary_filters(binary_filters_ids, binary_filters, filtered_df)
#     # getting a list of ids of all the bar charts
#     bar_Charts_ids = [id['id']['id'] for id in ctx.inputs_list[1]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_bar_chart_data(bar_Charts_ids, bar_charts_data, filtered_df)
#     # getting a list of ids of all the range sliders
#     range_sliders_ids = [id['id']['id'] for id in ctx.inputs_list[2]]
#     # filtering by the bar charts selected data
#     filtered_df = filter_by_range_slider(range_sliders_ids, range_sliders_data, filtered_df)
#     # Filtering the data by the start and end date from date picker
#     filtered_df = filtered_df[
#         (filtered_df['datetime']>=date_start) &
#         (filtered_df['datetime']<=date_end)
#     ]
#     stacked_bar_chart_figures_ids = [id['id'] for id in ctx.outputs_list]
#     stacked_bar_chart_figures = []
#     for chart_id in stacked_bar_chart_figures_ids:
#         filtered_df = filtered_df.groupby([chart_id['id'],chart_id['x_axis']],agg=chart_id['agg']).to_pandas_df()
#         stacked_bar_chart_figures.append(
#             stacked_bar_chart_figure(
#                 df = filtered_df,
#                 x_axis = chart_id['x_axis'],
#                 y_axis = chart_id['y_axis'],
#                 category = chart_id['id']
#             )
#         )
#     return stacked_bar_chart_figures
