import plotly.graph_objects as go
from dash import dcc, ctx, no_update, Input, Output, ALL
import uuid
import ast
from filter_manager import filter_manager


def horizontal_bar_chart_figure(values, categories, title=None, selected_points=None):
    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation='h',
            selectedpoints=selected_points
        )
    )
    fig.update_layout(
        dragmode='select',
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin={"t": 30, "b": 0, "r": 20, "l": 0, "pad": 0},
        title_text = title
    )
    fig.update_yaxes(title_text='outcome')
    return fig


def horizontal_bar_chart(categories, value_by, df, id=None, agg='count', title=None):
    id = str(uuid.uuid4()) if not id else id
    df = df.groupby([categories],agg=agg).to_pandas_df()
    df = df.sort_values(by=[value_by])
    return dcc.Graph(
        figure=horizontal_bar_chart_figure(
            categories=df[categories],
            values=df[value_by],
        ),
        responsive=True, 
        className="fill-parent-div sm-padding",
        id = {'type':'bar_chart', 'id':id, 'column_name':categories, 'value_by':value_by, 'agg':agg}
    )


############################################## For filter manager


# filtering by the bar charts selected data
@filter_manager.register_filter_functions('bar_chart')
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
@filter_manager.register_component_generator('bar_chart')
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


filter_manager.register_inputs_outputs(
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
    Output(
        {
            "type": "bar_chart",
            "id": ALL,
            "column_name": ALL,
            "value_by": ALL,
            "agg": ALL,
        },
        "figure",
    )
)