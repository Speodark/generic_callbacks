import vaex
import ast
import pandas as pd
import dash
from dash import Input, Output, ALL, ctx, no_update
from dash.exceptions import PreventUpdate
from components import horizontal_bar_chart_figure, stacked_bar_chart_figure
from pprint import pprint
import itertools
from .callbackFunctions import *

df = vaex.open("assets/data/data.hdf5")


##################################################### binary filters
# filtering by the binary filters
def filter_by_binary_filters(df, data):
    # going through all the binary filters ids
    for key, value in data.items():
        # checking if the binary filter been activated
        if value["children"]:
            # filtering the dataframe by the binary filter
            filter_id = ast.literal_eval(key)["column_name"]
            df = df[df[filter_id] == value["children"]]
    # Returning the df
    return df


##################################################### end


##################################################### bar charts
# filtering by the bar charts selected data
def filter_by_bar_chart(df, data, active_id=None):
    # going through all the bar charts ids
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)["column_name"]
            # checking if there are selected data
            if (
                data[filter_id]
                and data[filter_id]["selectedData"]
                and data[filter_id]["selectedData"]["points"]
            ):
                categories = []
                # going through each bar in the selected bar charts to get the choosen categories
                for bar in data[filter_id]["selectedData"]["points"]:
                    categories.append(bar["y"])
                # filtering the dataframe by the bar charts
                df = df[df[column_name].isin(categories)]
    return df


# Create bar charts outputs
def create_bar_chart_figure(dfs, component_data):
    trigger_id = ctx.triggered_id
    print(trigger_id, "NEW")
    bar_charts = []
    for bar_chart_id in dfs.keys():
        full_id = ast.literal_eval(bar_chart_id)
        if trigger_id == full_id:
            bar_charts.append(no_update)
        else:
            column_name = full_id["column_name"]
            agg_function = full_id["agg"]
            sort_by = full_id["value_by"]
            # Getting the dataframe ready for the chart
            dfs[bar_chart_id] = dfs[bar_chart_id].groupby([column_name], agg=agg_function)
            dfs[bar_chart_id] = (
                dfs[bar_chart_id].sort(sort_by).to_pandas_df().reset_index(drop=True)
            )
            # Getting selected points if there are any
            selected_points = None
            if (
                component_data[bar_chart_id]
                and component_data[bar_chart_id]["selectedData"]
                and component_data[bar_chart_id]["selectedData"]["points"]
            ):
                selected = [
                    point_index["y"]
                    for point_index in component_data[bar_chart_id]["selectedData"]["points"]
                ]
                selected_points = dfs[bar_chart_id][
                    dfs[bar_chart_id][column_name].isin(selected)
                ].index.values
            # creating the chart and appending it to the charts list
            bar_charts.append(
                horizontal_bar_chart_figure(
                    categories=dfs[bar_chart_id][column_name],
                    values=dfs[bar_chart_id][sort_by],
                    selected_points=selected_points,
                )
            )

    return bar_charts


##################################################### END


##################################################### date_picker_range
# Goes through all the date picker range and filter the dataframe by each of them except the active_id one.
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


##################################################### END


##################################################### Range sliders
# filtering by the range slider value
def filter_by_range_slider(df, data, active_id=None):
    for filter_id in data.keys():
        if filter_id != active_id:
            column_name = ast.literal_eval(filter_id)["column_name"]
            # checking if the value is not none
            value = data[filter_id]["value"]
            if value[0] is not None and value[1] is not None:
                # filtering the dataframe by the range slider value
                df = df[(df[column_name] >= value[0]) & (df[column_name] <= value[1])]
    return df


# Create the range sliders outputs
# IMPORTANT NOTE FOR LATER
# this component require two outputs, when we build the manager and add the outputs by decorator
# we need to make sure we return the values the same order we pass the outputs else it wont work.
def create_range_sliders(dfs, _):
    range_sliders_minimums = []
    range_sliders_maximums = []
    for range_slider_id in dfs.keys():
        column_name = ast.literal_eval(range_slider_id)["column_name"]
        range_sliders_minimums.append(int(dfs[range_slider_id][column_name].min()))
        range_sliders_maximums.append(int(dfs[range_slider_id][column_name].max()))
    return range_sliders_minimums, range_sliders_maximums


##################################################### END

##################################################### kpi
# create the kpi outputs (because kpi has only output and no input it gets one df for all kpis)
def create_kpi(df, components_data):
    kpis_values = []
    for kpi_id in components_data.keys():
        kpi_name = ast.literal_eval(kpi_id)["kpi_name"]
        if kpi_name == "animal_count":
            kpis_values.append(len(df))
        if kpi_name == "adopted":
            kpis_values.append(len(df[df.outcome_type == "Adoption"]))
    return kpis_values


##################################################### END

##################################################### stacked bar chart
# create the kpi outputs
# NOTE right now the stacked bar chart is an ouput only component means its not filtering
# later add filtering option. look at an earlier version to see the code for the create 
# from multiple dfs.
def create_stacked_bar_chart(df, components_data):
    stacked_bar_charts = []
    for chart_id in components_data.keys():
        temp_df = df.copy()
        full_id = ast.literal_eval(chart_id)
        column_name = full_id["column_name"]
        agg_function = full_id["agg"]
        x_axis = full_id["x_axis"]
        y_axis = full_id["y_axis"]
        # Getting the dataframe ready for the chart
        temp_df = temp_df.groupby(
            [column_name, x_axis], agg=agg_function
        ).to_pandas_df()

        stacked_bar_charts.append(
            stacked_bar_chart_figure(
                df=temp_df, x_axis=x_axis, y_axis=y_axis, category=column_name
            )
        )
    return stacked_bar_charts


##################################################### END

# for each type we have a filtering function
filter_functions = {
    "date_picker_range": filter_by_date_picker_range,
    "binary_filter": filter_by_binary_filters,
    "bar_chart": filter_by_bar_chart,
    "range_slider": filter_by_range_slider,
}


# output functions for each output type
generate_component_functions = {
    "date_picker_range": create_dpr_output,
    "bar_chart": create_bar_chart_figure,
    "range_slider": create_range_sliders,
    "kpi": create_kpi,
    "stacked_bar_chart": create_stacked_bar_chart,
}


##################################
# Check if order matters if it does make it so it doesn't matter!
##################################
@dash.callback(
    # date_picker_range outputs
    Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
    Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
    Output(
        {"type": "date_picker_range", "column_name": ALL, "id": ALL}, "min_date_allowed"
    ),
    Output(
        {"type": "date_picker_range", "column_name": ALL, "id": ALL}, "max_date_allowed"
    ),
    Output(
        {"type": "date_picker_range", "column_name": ALL, "id": ALL},
        "initial_visible_month",
    ),
    # bar_charts outputs
    Output(
        {
            "type": "bar_chart",
            "id": ALL,
            "column_name": ALL,
            "value_by": ALL,
            "agg": ALL,
        },
        "figure",
    ),
    # stacked_bar_charts outputs
    Output(
        {
            "type": "stacked_bar_chart",
            "id": ALL,
            "column_name": ALL,
            "x_axis": ALL,
            "y_axis": ALL,
            "agg": ALL,
        },
        "figure",
    ),
    # KPIS
    Output({"type": "kpi", "id": ALL, "kpi_name": ALL}, "children"),
    # range_sliders outputs
    Output({"type": "range_slider", "id": ALL, "column_name": ALL}, "min"),
    Output({"type": "range_slider", "id": ALL, "column_name": ALL}, "max"),
    # date_picker_range inputs
    Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
    Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
    # binary_filters inputs
    Input(
        {"type": "binary_filter", "id": ALL, "column_name": ALL, "sub_type": "value"},
        "children",
    ),
    # bar_charts Inputs
    Input(
        {
            "type": "bar_chart",
            "id": ALL,
            "column_name": ALL,
            "value_by": ALL,
            "agg": ALL,
        },
        "selectedData",
    ),
    # range_sliders Inputs
    Input({"type": "range_slider", "id": ALL, "column_name": ALL}, "value"),
    prevent_initial_call=True,
)
def dashboard_update(*args):
    # Get a list of all the types
    types = set(list(filter_functions.keys()) + list(generate_component_functions.keys()))
    # Create a dictionary with type as a key and empty dict as a value
    type_dict = {key: {} for key in types}


    # Update type_dict using the inputs_list
    update_type_dict_from_input_list(ctx.inputs_list, type_dict, args)
    # Update type_dict using the outputs_list and creating types_with_output_no_input list for 
    types_with_output_no_input, ordered_output_type_list = update_type_dict_from_output_list(ctx.outputs_list, type_dict, filter_functions)


    # we need to save the order with the empty outputs in order to return the components in the right order
    # because of that we create a new list for the ordrered output type list which will be used
    # to know which inputs dont have an output
    output_type_list = [
        output for output in ordered_output_type_list if output != "empty"
    ]


    # create a list of all the input and output types where the first types are the ones that doesnt have an output
    # because those who doesn't have an output only filter and don't change.
    # meaning i don't need to create multiple df so they won't effect themselfs
    input_type_list = list(type_dict.keys())
    input_without_output_types = list(set(input_type_list) - set(output_type_list))

    
    # remove all ids that appear in generate_component_functions and not in output_type_list from input_without_output_types
    # types that have output but do not appear in dashboard
    dont_have_output = list(set(generate_component_functions.keys()) - set(output_type_list))
    for output_type in dont_have_output:
        if output_type in input_without_output_types:
            input_without_output_types.remove(output_type)


    # This list will be ordered in order to optimize the df filtering
    # First the types that have an input and no output, means i only have to filter the main df
    # Second the output_type_list which have both the components with input and outputs 
    # Third will be the components that have an output but not an input
    # and components with only outputs 
    type_list = input_without_output_types.copy()
    type_list.extend(output_type_list)

    
    # Get the types that have an output and not an input to be last in the list
    # for optimization, we won't need to filter their dataframes because all the filters
    # has been done
    for component_type in types_with_output_no_input:
        type_list.remove(component_type)
    type_list.extend(types_with_output_no_input)


    # for each input type we go over all input types again and filter by them except for the current input_type.
    filtered_df = df
    individual_filtered_df = {}


    for component_type in type_list:

        # For each component/type we create an individual df depends on the sitation
        # 1: the type is does not filter we only need to create one df for all the components
        # 2: the type is does filter so we need to create df for each component in the type so
        #    we each component won't filter itself
        # 3: the type does not have an output, means we don't create a df because we don't create a component.
        create_df_for_individual_components(
            component_type,
            input_without_output_types,
            filter_functions,
            individual_filtered_df,
            type_dict,
            filtered_df
        )


        if component_type in filter_functions.keys():

            # Here we filter components that have both input and output, taking care they don't filter themself in the process
            components_input_and_output_filter(
                component_type,
                input_without_output_types,
                individual_filtered_df,
                filter_functions,
                type_dict
            )
        
            # Filter the df by all the components for the next input type
            # note only this part of the code will run if the type only has an input and not output
            filtered_df = filter_functions[component_type](
                df=filtered_df, data=type_dict[component_type]
            )

    # Creating the outputs list
    outputs = []
    for output_type in ordered_output_type_list:
        # if the output is empty (does not exsist in the dashboard) we need to append an empty list
        if output_type == "empty":
            outputs.append([]) # Switch to no_update
        else: 

            # If the component has an input and output, the generate function will get (dfs, components_data)
            # If the component has only an output, the generate function will get (df, components_data)
            components_of_type = generate_component_functions[output_type](
                individual_filtered_df[output_type],
                type_dict[output_type]
            )
            # check if components is a nested list (lists inside a list)
            # Happens if the components require more than 1 output to update like 
            # date_picker_range and range_sliders then we need to add to the list each component output
            is_nested = any(isinstance(component_arg, list) for component_arg in components_of_type)

            # if its a nested list we need to appened each arg individually
            # else we need to append all the components
            if is_nested:
                for component in components_of_type:
                    outputs.append(component)
            else:
                outputs.append(components_of_type)
    # returning the outputs Finishing the callback
    return outputs
