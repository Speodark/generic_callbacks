from dash import html


def card(id=None, className="", style={}, children=None, header=None):
    # If the card does not have children but does have a header
    # then create the header
    if not isinstance(children, list) and header:
        header = html.Span(
            className="card__header",
            children=header
        )
        children = [children]
        children.insert(0, header)
    elif isinstance(children, list) and header:
        children.insert(0, header)
    if id:
        return html.Div(
            id=id,
            className='card ' + className,
            style=style,
            children=children
        )
    else:
        return html.Div(
            className='card ' + className,
            style=style,
            children=children
        )
