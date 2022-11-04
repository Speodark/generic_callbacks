from dash import html, dcc
from dash import Input, Output, ALL, State, MATCH, ctx
import dash
import uuid
from filter_manager import filter_manager
import ast

def binary_filter(column_name, categories, colors, id=None, className = ''):
    id = str(uuid.uuid4()) if not id else id
    return html.Div(
        className='binary-filter ' + className,
        children=[
            html.Span(
                className='binary-filter__item binary-filter__item--1',
                children=categories[0],
                id= {'type':'binary_filter', 'column_name':column_name, 'sub_type':'category', 'index':categories[0], 'id':id},
                style={'background-color':colors[0]}
            ),
            html.Span(
                className='binary-filter__item binary-filter__item--2',
                children=categories[1],
                id= {'type':'binary_filter', 'column_name':column_name, 'sub_type':'category', 'index':categories[1], 'id':id},
                style={'background-color':colors[1]}
            ),
            html.Div(
                className='hide',
                children='',
                id= {'type':'binary_filter', 'column_name':column_name, 'sub_type':'value', 'id':id}
            )
        ]
    )


@dash.callback(
    Output({'type':'binary_filter', 'column_name':MATCH, 'id':MATCH, 'sub_type':'category', 'index':ALL}, 'style'), 
    Output({'type':'binary_filter', 'column_name':MATCH, 'id':MATCH, 'sub_type':'value'}, 'children'),
    Input({'type':'binary_filter', 'column_name':MATCH, 'id':MATCH, 'sub_type':'category', 'index':ALL}, 'n_clicks'),
    State({'type':'binary_filter', 'column_name':MATCH, 'id':MATCH, 'sub_type':'value'}, 'children'),
    State({'type':'binary_filter', 'column_name':MATCH, 'id':MATCH, 'sub_type':'category', 'index':ALL}, 'style'),
    prevent_initial_call=True
)
def binary_filter_callback(_, active_filter, styles):
    # Getting the index of who triggered the id, the index is the category clicked
    triggered_category = ctx.triggered_id['index']
    # getting all the categories
    categories = [category['id']['index'] for category in dash.callback_context.inputs_list[0]]
    # If the triggered category is in the active filter 
    # we only need to get rid of the blur
    # and return nothing to the value 
    if triggered_category in active_filter:
        for index in range(len(styles)):
            styles[index]['filter'] = ['none']
        return styles, ''
    else:
        # for the category that wasn't clicked we give a blur and return the clicked category to the value
        for index,category in enumerate(categories):
            if triggered_category==category:
                styles[index]['filter'] = 'none'     
            else:
                styles[index]['filter'] = 'blur(3px)'
        return styles, triggered_category


# For filter manager
@filter_manager.register_filter_functions('binary_filter')
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


filter_manager.register_inputs_outputs(
    Input(
        {"type": "binary_filter", "id": ALL, "column_name": ALL, "sub_type": "value"},
        "children",
    )
)