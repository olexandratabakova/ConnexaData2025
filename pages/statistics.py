from dash import html, dcc, Input, Output
from components.nav import NAV_COMPONENT

from config import FILTERED_OUTPUT_DIR
from styles.style import common_styles, h1_style, button_style_backtohome, description_style
from components.dropdown import create_dropdown
from utils.analysing_requests.statistics_calculations import *
logging.basicConfig(level=logging.ERROR)




layout = html.Div(
    style={**common_styles, 'padding': '0px', 'position': 'relative'},
    children=[
        NAV_COMPONENT,
        html.H1("ConnexaData", style=h1_style),
        html.Div(
            style={'marginTop': '0px', 'textAlign': 'center'},
            children=[
                html.P(
                    "This is a page with statistics about your texts (degree, mention of words in the text).",
                    style=description_style
                ),
                html.Div(
                    style={'width': '500px'},
                    children=[
                create_dropdown('file-selector')]
                ),
                html.Div(
                    id='output-container',
                    style={
                        'marginTop': '20px',
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'justifyContent': 'center',
                        'gap': '20px'
                    }
                )
            ]
        )
    ]
)


def register_callbacks(app):
    @app.callback(
        Output('output-container', 'children'),
        Input('file-selector', 'value')
    )
    def update_output(selected_filename):
        if not selected_filename:
            return html.Div("Please select a file.", style={'color': 'gray'})

        full_path = os.path.join(FILTERED_OUTPUT_DIR, selected_filename)

        if not os.path.exists(full_path):
            return html.Div("Selected file not found.", style={'color': 'gray'})

        try:
            counts = count_occurrences(full_path)
            influence = calculate_influence(full_path)

            visualizations = []
            if counts:
                visualizations.append(create_visualization(counts, "Most Frequent Objects", "#FCE7AB"))
            if influence:
                visualizations.append(create_visualization(influence, "Node Degrees", "#CEFCFF"))

            return visualizations or html.Div("No valid data found in selected file", style={'color': 'gray'})

        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            return html.Div("Error processing selected file", style={'color': 'red'})