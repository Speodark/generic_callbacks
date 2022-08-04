from dash import html

def kpi(id, text, value, className = ""):
    return html.Div(
        className='kpi ' + className,
        children=[
             html.Span(
                value,
                className='kpi__value',
                id = {'type':'kpi','id':id}
             ),
             html.Span(
                text,
                className='kpi__text'
             )
        ] 
    )