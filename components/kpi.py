from dash import html, Output, ALL
import uuid
import ast
from filter_manager import filter_manager

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


################################## For filter manager
@filter_manager.register_component_generator('kpi')
def create_kpi(df, components_data):
    kpis_values = []
    for kpi_id in components_data.keys():
        kpi_name = ast.literal_eval(kpi_id)["kpi_name"]
        if kpi_name == "animal_count":
            kpis_values.append(len(df))
        if kpi_name == "adopted":
            kpis_values.append(len(df[df.outcome_type == "Adoption"]))
    return kpis_values


filter_manager.register_inputs_outputs(
    Output({"type": "kpi", "id": ALL, "kpi_name": ALL}, "children")
)