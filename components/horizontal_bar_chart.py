import plotly.graph_objects as go
from dash import dcc


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


def horizontal_bar_chart(category_name, value_by, df, agg='count', title=None):
    df = df.groupby([category_name],agg=agg).to_pandas_df()
    df = df.sort_values(by=[value_by])
    return dcc.Graph(
        figure=horizontal_bar_chart_figure(
            categories=df[category_name],
            values=df[value_by],
        ),
        responsive=True, 
        className="fill-parent-div sm-padding",
        id = {'type':'bar_chart','id':category_name, 'value_by':value_by, 'agg':agg}
    )
