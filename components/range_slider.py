from dash import dcc, Input, Output, ALL
import uuid
import ast
from filter_manager import filter_manager

def range_slider(category, df, id=None):
    id = str(uuid.uuid4()) if not id else id
    return dcc.RangeSlider(
        min=int(df[category].min()),
        max=int(df[category].max()),
        step=1,
        value=[
            int(df[category].min()),
            int(df[category].max()),
        ],
        id={
            "type": "range_slider",
            "id": id,
            "column_name": category,
        },
    )


################################## For filter manager
# filtering by the range slider value
@filter_manager.register_filter_functions('range_slider')
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
@filter_manager.register_component_generator('range_slider')
def create_range_sliders(dfs, _):
    range_sliders_minimums = []
    range_sliders_maximums = []
    for range_slider_id in dfs.keys():
        column_name = ast.literal_eval(range_slider_id)["column_name"]
        range_sliders_minimums.append(int(dfs[range_slider_id][column_name].min()))
        range_sliders_maximums.append(int(dfs[range_slider_id][column_name].max()))
    return range_sliders_minimums, range_sliders_maximums


filter_manager.register_inputs_outputs(
    Output({"type": "range_slider", "id": ALL, "column_name": ALL}, "min"),
    Output({"type": "range_slider", "id": ALL, "column_name": ALL}, "max"),
    Input({"type": "range_slider", "id": ALL, "column_name": ALL}, "value"),
)