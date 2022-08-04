from dash import html, dcc
from dash import Input, Output, ALL, State, MATCH, ctx
import dash


def binary_filter(id, categories, colors, className = ''):
    return html.Div(
        className='binary-filter ' + className,
        children=[
            html.Span(
                className='binary-filter__item binary-filter__item--1',
                children=categories[0],
                id= {'type':'binary_filter','id':id, 'sub_type':'category', 'index':categories[0]},
                style={'background-color':colors[0]}
            ),
            html.Span(
                className='binary-filter__item binary-filter__item--2',
                children=categories[1],
                id= {'type':'binary_filter','id':id, 'sub_type':'category', 'index':categories[1]},
                style={'background-color':colors[1]}
            ),
            html.Div(
                className='hide',
                children='',
                id= {'type':'binary_filter','id':id, 'sub_type':'value'}
            )
        ]
    )


@dash.callback(
    Output({'type':'binary_filter','id':MATCH, 'sub_type':'category', 'index':ALL}, 'style'), 
    Output({'type':'binary_filter','id':MATCH, 'sub_type':'value'}, 'children'),
    Input({'type':'binary_filter','id':MATCH, 'sub_type':'category', 'index':ALL}, 'n_clicks'),
    State({'type':'binary_filter','id':MATCH, 'sub_type':'value'}, 'children'),
    State({'type':'binary_filter','id':MATCH, 'sub_type':'category', 'index':ALL}, 'style'),
    prevent_initial_call=True
)
def binary_filter_callback(_, active_filter, styles):
    triggered_category = ctx.triggered_id['index']
    categories_indexs = [category['id']['index'] for category in dash.callback_context.inputs_list[0]]
    if triggered_category in active_filter:
        for ind in range(len(styles)):
            styles[ind]['filter'] = ['none']
        return styles, ''
    else:
        for ind,category in enumerate(categories_indexs):
            if triggered_category==category:
                styles[ind]['filter'] = 'none'     
            else:
                styles[ind]['filter'] = 'blur(3px)'
        return styles, triggered_category
