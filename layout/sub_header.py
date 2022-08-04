from dash import html
from components import binary_filter, kpi


def sub_header(df, className=''):
    return html.Div(
        className = 'sub-header ' + className,
        children=[
            kpi(
                text='Animal Count', 
                value=len(df),
                className='sub-header__animal-count',
                id = 'animal_count'
            ),
            kpi(
                text='Adopted', 
                value=len(df[df.outcome_type == 'Adoption']),
                className='sub-header__adopted',
                id = 'adopted'
            ),
            binary_filter(
                id = 'sex',
                categories=['Male','Female'],
                colors=['pink','#2B80FF'],
                className='sub-header__gender'
            ),
            binary_filter(
                id = 'castrated',
                categories=['castrated','not castrated'],
                colors=['green','red'],
                className='sub-header__castrated'
            )
        ]
    )