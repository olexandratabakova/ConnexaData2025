from dash import dcc, html, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import threading
import os
import dash_bootstrap_components as dbc
import base64

from styles.style import common_styles, h1_style, style_alert_base, description_style, button_style, button_style2, text_content_style, button_style_backtohome
from config import TEXT_FILE_PATH, OUTPUT_DIR, FILTERED_OUTPUT_DIR

from utils.analysing.analysis import *
from utils.analysing.filtering import filter_row
from utils.documents.converting_documents import *
from components.nav import NAV_COMPONENT

analysis_running = False
analysis_stop_event = threading.Event()
progress = 0
selected_model = "llama-3.3-70b-versatile"

os.makedirs(FILTERED_OUTPUT_DIR, exist_ok=True)


def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

file_list = get_file_list(os.path.dirname(TEXT_FILE_PATH))

layout = html.Div(
    style={**common_styles, 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'},
    children=[
        html.H1("ConnexaData", style={**h1_style, 'textAlign': 'center'}),
        html.Div(children=["This is the document page."], style=description_style),

        html.Div(
            style={'display': 'flex', 'flexDirection': 'row', 'marginTop': '20px', 'flex': '1'},
            children=[
                html.Div(
                    style={
                        'flex': '0.7',
                        'padding': '10px',
                        'borderRight': '1px solid #ccc',
                        'backgroundColor': '#f9f9f9'
                    },
                    children=[
                        NAV_COMPONENT,
                        dcc.Dropdown(
                            id='file-dropdown',
                            options=[{'label': file, 'value': file} for file in file_list],
                            value=file_list[0] if file_list else None,
                            style={'width': '100%', 'marginBottom': '20px', 'fontSize': '14px'}
                        ),
                        dcc.Upload(
                            id='upload-file',
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select Files", style={'color': '#007acc', 'textDecoration': 'underline'})
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0',
                                'backgroundColor': 'white',
                                'color': 'black'
                            },
                            multiple=False,
                            accept='.txt,.pdf,.docx',
                            max_size=5 * 1024 * 1024,
                        ),
                        dbc.Alert(
                            id='upload-error',
                            color="danger",
                            is_open=False,
                            duration=4000,
                            style=style_alert_base
                        ),
                        html.Div(
                            style={'display': 'flex', 'flexDirection': 'column', 'marginTop': '10px'},
                            children=[
                                html.Div([
                                    dcc.RadioItems(
                                        id='model-selector',
                                        options=[
                                            {'label': 'llama-3.3-70b-versatile', 'value': 'llama-3.3-70b-versatile'},
                                            {'label': 'gpt-4o-mini', 'value': 'gpt-4o-mini'}
                                        ],
                                        value=selected_model,
                                        labelStyle={'display': 'block', 'marginBottom': '10px'},
                                        style = {'textAlign':'left'}
                                    )
                                ]),
                                html.Button("Find connections between", id="run-analysis-related-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Discover related people by name", style={'marginBottom': '20px'}),
                                html.Button("Discover influential", id="run-analysis-influential-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Identify the most influential individuals", style={'marginBottom': '20px'}),
                                html.Button("Find related concepts", id="run-analysis-related-concepts-button",
                                            style={**button_style, 'border': 'none', 'marginBottom': '10px'}),
                                html.Div("Discover related concepts", style={'marginBottom': '20px'}),
                                html.Button("Stop Analysis", id="stop-analysis-button",
                                            style={**button_style2, 'border': 'none', 'display': 'none',
                                                   'marginLeft': '10px'})
                            ]
                        ),
                    ]
                ),

                html.Div(
                    style={
                        'flex': '2.3',
                        'padding': '10px',
                        'backgroundColor': 'white'
                    },
                    children=[
                        html.Div(
                            style={
                                'border': '1px solid #ccc',
                                'padding': '10px',
                                'overflow': 'auto',
                                'maxHeight': '500px',
                                'backgroundColor': 'white'
                            },
                            children=[
                                html.Div(id='text-content', style=text_content_style)
                            ]
                        ),
                        html.Div(
                            style={'marginTop': '10px'},
                            children=[
                                html.Div(id='file-info', style={'fontSize': '14px', 'color': '#555'})
                            ]
                        )
                    ]
                ),
            ]
        ),

        html.Div(
            id='progress-container',
            style={'display': 'none', 'marginTop': '20px'},
            children=[
                html.Div("Progress:", style={'fontWeight': 'bold'}),
                html.Div(id='progress-bar', style={'width': '0%', 'height': '20px', 'backgroundColor': '#007acc'}),
                html.Div(id='progress-text', style={'marginTop': '10px'})
            ]
        ),

        dcc.Interval(
            id='progress-interval',
            interval=1000,
            n_intervals=0,
            disabled=True
        ),
    ]
)

def process_text_chunks(file_path, output_dir, request_function, chunk_size=2400):
    global analysis_running, analysis_stop_event, progress
    analysis_running = True
    progress = 0
    original_filename = os.path.basename(file_path)
    output_filename = f"output_{request_function.__name__}_{original_filename}"
    output_file = os.path.join(output_dir, output_filename)
    filtered_output_filename = f"filtered_{output_filename}"
    filtered_output_file = os.path.join(FILTERED_OUTPUT_DIR, filtered_output_filename)

    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().replace('\n', ' ')
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(FILTERED_OUTPUT_DIR):
        os.makedirs(FILTERED_OUTPUT_DIR)

    with open(output_file, "w", encoding='utf-8') as output_file, open(filtered_output_file, "w", encoding='utf-8') as filtered_file:
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            if analysis_stop_event.is_set():
                break

            result = request_function(chunk, selected_model)
            output_file.write(result + "\n")
            filtered_result = "\n".join([line for line in result.split("\n") if filter_row(line)])
            filtered_file.write(filtered_result + "\n")
            progress = int((i + 1) / total_chunks * 100)
    analysis_running = False
    analysis_stop_event.clear()
    return output_file
def register_callbacks(app):
    @app.callback(
        [Output('file-dropdown', 'options'),
         Output('file-dropdown', 'value'),
         Output('upload-error', 'children'),
         Output('upload-error', 'is_open')],
        [Input('upload-file', 'contents')],
        [State('upload-file', 'filename'),
         State('upload-file', 'last_modified')]
    )
    def upload_and_convert_file(contents, filename, last_modified):
        if contents is None:
            raise PreventUpdate

        try:
            upload_dir = os.path.dirname(TEXT_FILE_PATH)

            content_type, content_string = contents.split(',')
            upload_path = os.path.join(upload_dir, filename)
            with open(upload_path, 'wb') as f:
                f.write(base64.b64decode(content_string))

            text_content = process_uploaded_file(upload_path)
            if len(text_content) > 30000:
                os.remove(upload_path)
                raise ValueError(f"Файл перевищує ліміт у 30000 символів")

            converted_file_path = convert_to_txt(upload_path, upload_dir)

            file_list = get_file_list(upload_dir)
            return (
                [{'label': file, 'value': file} for file in file_list],
                os.path.basename(converted_file_path),
                "",
                False
            )

        except ValueError as e:
            return (
                no_update,
                no_update,
                f"Помилка: {str(e)}",
                True
            )
        except Exception as e:
            return (
                no_update,
                no_update,
                f"Неочікувана помилка: {str(e)}",
                True
            )

    @app.callback(
        [Output('text-content', 'children'),
         Output('file-info', 'children')],
        [Input('file-dropdown', 'value')]
    )
    def display_selected_file_content(selected_file):
        if not selected_file:
            return "No file selected.", ""

        file_path = os.path.join(os.path.dirname(TEXT_FILE_PATH), selected_file)
        content = read_text_file(file_path)

        word_count = len(content.split())

        file_info = f"File: {selected_file} | Words: {word_count}"

        return content, file_info

    @app.callback(
        [Output('progress-container', 'style'),
         Output('progress-bar', 'style'),
         Output('progress-text', 'children'),
         Output('progress-interval', 'disabled'),
         Output('stop-analysis-button', 'style')],
        [Input('run-analysis-related-button', 'n_clicks'),
         Input('run-analysis-influential-button', 'n_clicks'),
         Input('run-analysis-related-concepts-button', 'n_clicks'),
         Input('stop-analysis-button', 'n_clicks'),
         Input('progress-interval', 'n_intervals')],
        State('file-dropdown', 'value')
    )
    def update_progress(related_clicks, influential_clicks, related_concepts_clicks, stop_clicks, n_intervals,
                        selected_file):
        global analysis_running, progress

        ctx = callback_context
        if not ctx.triggered:
            return {'display': 'none'}, {'width': '0%'}, "0%", True, {'display': 'none'}

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id in ['run-analysis-related-button', 'run-analysis-influential-button',
                          'run-analysis-related-concepts-button']:
            if not selected_file:
                return {'display': 'none'}, {'width': '0%'}, "Please select a file first.", True, {'display': 'none'}

            file_path = os.path.join(os.path.dirname(TEXT_FILE_PATH), selected_file)
            if trigger_id == 'run-analysis-related-button':
                analysis_thread = threading.Thread(target=process_text_chunks,
                                                   args=(file_path, OUTPUT_DIR, request_related_people))
            elif trigger_id == 'run-analysis-influential-button':
                analysis_thread = threading.Thread(target=process_text_chunks,
                                                   args=(file_path, OUTPUT_DIR, request_the_most_influential_people))
            elif trigger_id == 'run-analysis-related-concepts-button':
                analysis_thread = threading.Thread(target=process_text_chunks,
                                                   args=(file_path, OUTPUT_DIR, request_related_concepts))

            analysis_thread.start()

            return {'display': 'block'}, {'width': '0%'}, "0%", False, {'display': 'block', **button_style2}

        elif trigger_id == 'stop-analysis-button':
            if analysis_running:
                analysis_stop_event.set()
                return {'display': 'block'}, {'width': '100%',
                                              'backgroundColor': '#ff4d4d'}, "Analysis stopped by user.", True, {
                    'display': 'none'}
            else:
                return {'display': 'none'}, {'width': '0%'}, "No analysis is running.", True, {'display': 'none'}

        elif trigger_id == 'progress-interval':
            if analysis_running:
                return {'display': 'block'}, {'width': f'{progress}%',
                                              'backgroundColor': '#007acc'}, f"{progress}%", False, {'display': 'block', **button_style2}
            else:
                return {'display': 'none'}, {'width': '0%'}, "", True, {'display': 'none'}

        return {'display': 'none'}, {'width': '0%'}, "", True, {'display': 'none'}

    @app.callback(
        Output('model-selector', 'value'),
        [Input('model-selector', 'value')]
    )
    def update_model_selection(model):
        global selected_model
        selected_model = model
        return selected_model


    return app