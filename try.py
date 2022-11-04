from filter_manager import filter_manager
import dash
from dash import Output, Input, ALL

# Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
#     Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
#     Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
#     Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),

@filter_manager.register_component_generator('date_picker_range')
def _(dfs, hello):
    return dfs, hello


@filter_manager.register_filter_functions('date_picker_range')
def _(df, data, active_id=None):
    return df, data, active_id

filter_manager.register_inputs_outputs(
    Output({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "end_date"),
    Input({"type": "date_picker_range", "column_name": ALL, "id": ALL}, "start_date"),
)
print(filter_manager._generate_component_functions['date_picker_range']('hi','hello'))
print(filter_manager._filter_functions['date_picker_range']('hi','hello','nice'))
print(filter_manager._inputs)
print(filter_manager._outputs)