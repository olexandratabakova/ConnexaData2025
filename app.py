import dash
import time
from dash import dcc, html
from dash.dependencies import Input, Output
from pages import main, help_page, document, document_AbstractRequests, document_requests, table, table_influence, visualization, statistics

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Loading(
            id="loading",
            type="default",
            color="#1B5E67",
            children=[html.Div(id='page-content')],
            style={
                "position": "fixed",
                "top": "50%",
                "left": "50%",
                "transform": "translate(-50%, -50%)"
            }
        )
    ])
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    time.sleep(0.5)
    if pathname == '/help':
        return help_page.layout
    elif pathname == '/document':
        return document.layout
    elif pathname == '/table':
        return table.layout
    elif pathname == '/table_influence':
        return table_influence.layout
    elif pathname == '/statistics':
        return statistics.layout
    elif pathname == '/document_AbstractRequests':
        return document_AbstractRequests.layout
    elif pathname == '/document_requests':
        return document_requests.layout
    elif pathname == '/visualization':
        return visualization.layout
    else:
        return main.layout

document.register_callbacks(app)
document_AbstractRequests.register_callbacks(app)
document_requests.register_callbacks(app)


table.register_callbacks(app)
visualization.register_callbacks(app)
table_influence.register_callbacks(app)
statistics.register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)
