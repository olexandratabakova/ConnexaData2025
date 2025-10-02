from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from components.nav import NAV_COMPONENT
from styles.style import common_styles, h1_style, description_style, button_style

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},
    children=[
        html.H1("ConnexaData", style={**h1_style, 'textAlign': 'center', 'margin': '60px 0 30 0'}),
        html.Div(
            children=["Use the buttons below to either select from existing templates or create your own queries. Explore connections, patterns, and insights from your text in a few clicks."],
            style={**description_style, 'width': '800px'}
        ),
        NAV_COMPONENT,
        html.Div(
            style={
                'display': 'flex',
                'flexDirection': 'row',
                'marginTop': '30px',
                'justifyContent': 'center',
                'gap': '100px',
                'width': '100%',
                'maxWidth': '800px'
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '300px'},
                    children=[
                        html.A(
                            "Choose Template",
                            href="/document_requests",
                            id="choose-template",
                            style={**button_style, 'border': 'none', 'marginBottom': '15px', 'width': '100%', 'padding': '10px', 'fontSize': '24px'}
                        ),
                        html.Div(
                            "Quickly pick from pre-made prompts that are already set up in the system. Ideal if you want fast results without typing your own query.",
                            style={'marginBottom': '20px'},
                            id="choose-template-output"
                        )
                    ]
                ),
                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '300px'},
                    children=[
                        html.A(
                            "Create Your Own",
                            href="/document_AbstractRequests",
                            id="create-your-own",
                            style={**button_style, 'border': 'none', 'marginBottom': '15px', 'width': '100%', 'padding': '10px', 'fontSize': '24px'}
                        ),
                        html.Div(
                            "Type in your own request and generate a custom prompt. Perfect for when you have a specific idea or need something unique.",
                            style={'marginBottom': '20px'},
                            id="create-your-own-output"
                        )
                    ]
                )
            ]
        )
    ]
)


def register_callbacks(app):
    return app