from dash import html
import uuid

def kpi(kpi_name, text, value, id = None, className = ""):
    id = str(uuid.uuid4()) if not id else id
    return html.Div(
        className='kpi ' + className,
        children=[
             html.Span(
                value,
                className='kpi__value',
                id = {'type':'kpi','id':id, 'kpi_name':kpi_name}
             ),
             html.Span(
                text,
                className='kpi__text'
             )
        ] 
    )