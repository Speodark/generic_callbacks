import vaex
import ast
import pandas as pd
import dash
from dash import Input, Output, ALL, State, MATCH, ctx, no_update
from dash.exceptions import PreventUpdate
from components import (
    horizontal_bar_chart_figure,
    stacked_bar_chart_figure
)

df = vaex.open('assets/data/data.hdf5')


##################################################### binary filters
# filtering by the binary filters
def filter_by_binary_filters(df, data):
    # going through all the binary filters ids
    for key, value in data.items():
        # checking if the binary filter been activated
        if value['children']:
            # filtering the dataframe by the binary filter
            filter_id = ast.literal_eval(key)['column_name']
            df = df[df[filter_id]== value['children']]
    # Returning the df
    return df
##################################################### end


##################################################### bar charts
# filtering by the bar charts selected data
def filter_by_bar_chart(df, data, active_id = None):
    # going through all the bar charts ids
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)['column_name']
            # checking if there are selected data
            if data[filter_id] and data[filter_id]['selectedData'] and data[filter_id]['selectedData']['points']:
                categories = []
                # going through each bar in the selected bar charts to get the choosen categories
                for bar in data[filter_id]['selectedData']['points']:
                    categories.append(bar['y'])
                # filtering the dataframe by the bar charts
                df = df[df[column_name].isin(categories)]
    return df
# Create bar charts outputs
def create_bar_chart_figures(dfs, data):
    bar_charts = []
    for bar_chart_id in dfs.keys():
        full_id = ast.literal_eval(bar_chart_id)
        column_name = full_id['column_name']
        agg_function = full_id['agg']
        sort_by = full_id['value_by']
        # Getting the dataframe ready for the chart
        dfs[bar_chart_id] = dfs[bar_chart_id].groupby([column_name],agg=agg_function)
        dfs[bar_chart_id] = dfs[bar_chart_id].sort(sort_by).to_pandas_df().reset_index(drop=True)
        # Getting selected points if there are any
        selected_points = None
        if data[bar_chart_id] and data[bar_chart_id]['selectedData'] and data[bar_chart_id]['selectedData']['points']:
            selected = [point_index['y'] for point_index in data[bar_chart_id]['selectedData']['points']]
            selected_points = dfs[bar_chart_id][dfs[bar_chart_id][column_name].isin(selected)].index.values
        # creating the chart and appending it to the charts list
        bar_charts.append(
            horizontal_bar_chart_figure(
                categories=dfs[bar_chart_id][column_name],
                values=dfs[bar_chart_id][sort_by],
                selected_points=selected_points
            )
        )

    return bar_charts
##################################################### END


##################################################### date_picker_range
# Goes through all the date picker range and filter the dataframe by each of them except the active_id one.
def filter_by_date_picker_range(df, data, active_id = None):
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)['column_name']
            start_date = data[filter_id]['start_date']
            end_date = data[filter_id]['end_date']
            df = df[
                (df[column_name]>=start_date) &
                (df[column_name]<=end_date)
            ]
            
    return df
# Create date_picker_range outputs
def create_dpr_output(dfs, data):
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
        column_name = ast.literal_eval(dpr_id)['column_name']

        # get the minimum and maximum dates, we have to convert them from numpy array to pandas datetime.
        min_date, max_date = pd.to_datetime(dfs[dpr_id][column_name].min()), pd.to_datetime(dfs[dpr_id][column_name].max())
        # Check if the min date is lower then current date same with max
        start_date, end_date = pd.to_datetime(data[dpr_id]['start_date']), pd.to_datetime(data[dpr_id]['end_date'])
        start_date = start_date if start_date >= min_date else min_date 
        end_date = end_date if end_date <= max_date else max_date
        # Append the variables
        start_dates.append(start_date)
        end_dates.append(end_date)
        min_date_alloweds.append(min_date)
        max_date_alloweds.append(max_date)
        initial_visible_months.append(end_date)
    return start_dates, end_dates, min_date_alloweds, max_date_alloweds, initial_visible_months
##################################################### END


##################################################### Range sliders
# filtering by the range slider value
def filter_by_range_slider(df, data, active_id = None):
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)['column_name']
            # checking if the value is not none
            value = data[filter_id]['value']
            if value[0] is not None and value[1] is not None:
                # filtering the dataframe by the range slider value
                df = df[
                    (df[column_name] >= value[0]) &
                    (df[column_name] <= value[1])
                ]
    return df
# Create the range sliders outputs
def create_range_sliders(dfs, data):
    range_sliders_minimums = []
    range_sliders_maximums = []
    for range_slider_id in dfs.keys():
        column_name = ast.literal_eval(range_slider_id)['column_name']
        range_sliders_minimums.append(int(dfs[range_slider_id][column_name].min()))
        range_sliders_maximums.append(int(dfs[range_slider_id][column_name].max()))
    return range_sliders_minimums, range_sliders_maximums
##################################################### END

##################################################### kpi
# create the kpi outputs
def create_kpi(dfs, data):
    kpis_values = []
    for kpi_id in dfs.keys():
        kpi_name = ast.literal_eval(kpi_id)['kpi_name']
        if kpi_name == 'animal_count':
            kpis_values.append(len(dfs[kpi_id]))
        if kpi_name == 'adopted':
            kpis_values.append(len(dfs[kpi_id][dfs[kpi_id].outcome_type == 'Adoption']))
    return kpis_values
##################################################### END


# for each type we have a filtering function
type_filter_functions = {
    'date_picker_range': filter_by_date_picker_range,
    'binary_filter': filter_by_binary_filters,
    'bar_chart':filter_by_bar_chart,
    'range_slider': filter_by_range_slider
}


# output functions for each output type
output_type_functions = {
    'date_picker_range': create_dpr_output,
    'bar_chart': create_bar_chart_figures,
    'range_slider': create_range_sliders,
    'kpi': create_kpi
}


##################################
# Check if order matters if it does make it so it doesn't matter!
##################################
@dash.callback(
    # date_picker_range outputs
    Output({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'start_date'),
    Output({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'end_date'),
    Output({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'min_date_allowed'),
    Output({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'max_date_allowed'),
    Output({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'initial_visible_month'),
    # bar_charts outputs
    Output({'type':'bar_chart','id':ALL, 'column_name':ALL, 'value_by':ALL, 'agg':ALL}, 'figure'),
    # range_sliders outputs
    Output({'type':'range_slider','id':ALL, 'column_name':ALL}, 'min'),
    Output({'type':'range_slider','id':ALL, 'column_name':ALL}, 'max'),
    # KPIS
    Output({'type':'kpi','id':ALL, 'kpi_name':ALL}, 'children'),
    # date_picker_range inputs
    Input({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'start_date'),
    Input({'type': 'date_picker_range', 'column_name':ALL, 'id': ALL}, 'end_date'),
    # binary_filters inputs
    Input({'type': 'binary_filter', 'id': ALL, 'column_name':ALL, 'sub_type': 'value'}, 'children'),
    # bar_charts Inputs
    Input({'type':'bar_chart','id':ALL, 'column_name':ALL, 'value_by':ALL, 'agg':ALL},'selectedData'),
    # range_sliders Inputs
    Input({'type':'range_slider','id':ALL, 'column_name':ALL}, 'value'),
    prevent_initial_call=True
)
def dashboard_update(*args):
    # Get a list of all the types
    types = list(set(list(type_filter_functions.keys()) + list(output_type_functions.keys())))
    # Create a dictionary with type as a key and empty dict as a value
    type_dict = {key: {} for key in types}
    

    # gets the dictionary of dictionaries of all the Inputs type and values
    # the value of type_dict will look like this:
    # type_dict = {
    #   type: {
    #     full_id_1: {
    #       property1: value,
    #       property2: value
    #     }
    #   }
    # }
    for callback_input_index, callback_input in enumerate(ctx.inputs_list):
        for input_id_index, input_id in enumerate(callback_input):
            try:
                type_dict[input_id['id']['type']
                          ][str(input_id['id'])][input_id['property']] = args[callback_input_index][input_id_index]
            except:
                type_dict[input_id['id']['type']][str(input_id['id'])] = {
                    input_id['property']: args[callback_input_index][input_id_index]
                }


    # adds dictionaries of all outputs type and values that doesn't have an input to the type_dict
    # the value is null because there are no args for output
    for callback_input in ctx.outputs_list:
        for output_id in callback_input:
            if output_id['id']['type'] not in type_filter_functions.keys():
                try:
                    type_dict[output_id['id']['type']
                            ][str(output_id['id'])][output_id['property']] = ''
                except:
                    type_dict[output_id['id']['type']][str(output_id['id'])] = {
                        output_id['property']: ''
                    }


    # get all unique output types
    output_type_list_order = []
    for output in ctx.outputs_list:
        if not output:
            output_type_list_order.append('empty')
        for output_id in output:
            if output_id['id']['type'] not in output_type_list_order:
                output_type_list_order.append(output_id['id']['type'])
            break
    # we need to save the order with the empty outputs in order to return the components
    # in the right order and so we create a new list for the ordrered type list
    output_type_list = [output for output in output_type_list_order if output != 'empty']


    # create a list of all the input and output types where the first types are the ones that doesnt have an output
    # because those who doesn't have an output only filter and don't change.
    # meaning i don't need to create multiple df so they won't effect themselfs
    input_type_list = list(type_dict.keys())
    input_without_output_types = list(set(input_type_list) - set(output_type_list))
    # remove all ids that appear in output_type_functions and not in output_type_list from input_without_output_types
    # types that have output but do not appear in dashboard
    dont_have_output = list(set(output_type_functions.keys()) - set(output_type_list))
    for output_type in dont_have_output:
        if output_type in input_without_output_types:
            input_without_output_types.remove(output_type)
    # Add the inputs without outputs to the type list
    type_list = input_without_output_types.copy()
    type_list.extend(output_type_list)

    
    # for each input type we go over all input types again and filter by them except for the current input_type.
    filtered_df = df
    individual_filtered_df = {}
    for component_type in type_list:
        # handling component type that have an output but not an input (means it doesn't filter!)
        if component_type not in type_filter_functions.keys():
            # create the type in the dictioanry
            individual_filtered_df[component_type] = {}
            # for each different input component in that specific type create a key and copy the filtered_df
            for key in type_dict[component_type].keys():
                individual_filtered_df[component_type][key] = filtered_df
        else:
            # checking the input has an output if it does then we need to create a df for each component in the type
            # and filter all of the exsisting dfs
            if component_type not in input_without_output_types:
                # create the type in the dictioanry
                individual_filtered_df[component_type] = {}
                # for each different input component in that specific type create a key and copy the filtered_df
                for key in type_dict[component_type].keys():
                    individual_filtered_df[component_type][key] = filtered_df
                # filter each filtered df by all the different components by the type components
                for filtered_df_type in individual_filtered_df.keys():
                    for filtered_df_key in individual_filtered_df[filtered_df_type].keys():
                        # update the df to the filtered one by the component filter function
                        # The filtering function is the one in the component_type key.
                        individual_filtered_df[filtered_df_type][filtered_df_key] = \
                            type_filter_functions[component_type](
                                df=individual_filtered_df[filtered_df_type][filtered_df_key], 
                                data=type_dict[component_type], 
                                active_id = filtered_df_key
                            )
            # Filter the df by all the components for the next input type
            # note only this part of the code will run if the type only has an input and not output
            filtered_df = type_filter_functions[component_type](
                df=filtered_df, 
                data=type_dict[component_type]
            )


    # Creating the outputs list
    outputs = []
    for output_type in output_type_list_order:
        # if the output is empty (does not exsist in the dashboard) we need to append an empty list
        if output_type == 'empty':
            outputs.append([])
        else:
            args = output_type_functions[output_type](
                dfs = individual_filtered_df[output_type],
                data = type_dict[output_type]
            )
            # check if args is a nested list (lists inside a list)
            is_nested = any(isinstance(arg, list) for arg in args)
            # if its a nested list we need to appened each arg individually
            # else we need to append all the args
            if is_nested:
                for arg in args:
                    outputs.append(arg)
            else:
                outputs.append(args)


    # returning the outputs Finishing the callback
    return outputs
