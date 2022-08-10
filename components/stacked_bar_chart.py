import plotly.express as px
from dash import dcc
import uuid

def stacked_bar_chart_figure(df, x_axis, y_axis, category):
    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        color = category
    )
    fig.update_layout(
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        legend=dict(
            orientation="h",
            yanchor="middle",
            y=1.1,
            xanchor="center",
            x=0.5,
            title={'text': None}
        ),
        margin={"t": 30, "b": 0, "r": 20, "l": 0, "pad": 0},
    )
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig




def stacked_bar_chart(x_axis, y_axis, category, df, id=None, agg='count'):
    id = str(uuid.uuid4()) if not id else id
    df = df.groupby([category, x_axis],agg=agg).to_pandas_df()
    return dcc.Graph(
        figure=stacked_bar_chart_figure(
            df = df,
            x_axis = x_axis,
            y_axis=y_axis,
            category=category
        ),
        responsive=True, 
        className="fill-parent-div sm-padding",
        id = {'type':'stacked_bar_chart','id':id, 'column_name':category, 'x_axis':x_axis, 'y_axis':y_axis, 'agg':agg}
    )