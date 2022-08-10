import plotly.graph_objects as go
from dash import dcc
import uuid


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
