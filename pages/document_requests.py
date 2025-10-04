from dash import dcc, html, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import threading
import dash_bootstrap_components as dbc
from styles.document_requests_style import *
from config import TEXT_FILE_PATH, OUTPUT_DIR, FILTERED_OUTPUT_DIR

from utils.analysing_requests.analysis_requests import *
from utils.analysing_requests.filtering import filter_row
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
    style=layout_style,
    children=[
        html.H1("ConnexaData", style=h1_centered_style),
        html.Div(children=["This is the document page."], style=description_style),

        html.Div(
            style=main_container_style,
            children=[
                html.Div(
                    style=left_panel_style,
                    children=[
                        NAV_COMPONENT,
                        dcc.Dropdown(
                            id='file-dropdown',
                            options=[{'label': file, 'value': file} for file in file_list],
                            value=file_list[0] if file_list else None,
                            style=dropdown_style
                        ),
                        dcc.Upload(
                            id='upload-file',
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select Files", style={'color': '#007acc', 'textDecoration': 'underline'})
                            ]),
                            style=upload_style,
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
                            style=button_column_style,
                            children=[
                                html.Div([
                                    dcc.RadioItems(
                                        id='model-selector',
                                        options=[
                                            {'label': 'llama-3.3-70b-versatile', 'value': 'llama-3.3-70b-versatile'},
                                            {'label': 'gpt-4o-mini', 'value': 'gpt-4o-mini'},
                                        ],
                                        value=selected_model,
                                        labelStyle=radio_label_style,
                                        style=radio_style
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
                                            style=stop_button_hidden_style)
                            ]
                        ),
                    ]
                ),

                html.Div(
                    style=right_panel_style,
                    children=[
                        html.Div(
                            style=text_container_style,
                            children=[
                                html.Div(id='text-content', style=text_content_style)
                            ]
                        ),
                        html.Div(
                            style={'marginTop': '10px'},
                            children=[
                                html.Div(id='file-info', style=file_info_style)
                            ]
                        )
                    ]
                ),
            ]
        ),

        html.Div(
            id='progress-container',
            style=progress_container_style,
            children=[
                html.Div("Progress:", style=progress_label_style),
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
    output_file_path = os.path.join(output_dir, output_filename)
    filtered_output_filename = f"filtered_{output_filename}"
    filtered_output_file = os.path.join(FILTERED_OUTPUT_DIR, filtered_output_filename)

    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().replace('\n', ' ')
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(FILTERED_OUTPUT_DIR):
        os.makedirs(FILTERED_OUTPUT_DIR)

    with open(output_file_path, "w", encoding='utf-8') as output_file, open(filtered_output_file, "w",
                                                                            encoding='utf-8') as filtered_file:
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            if analysis_stop_event.is_set():
                break

            result = request_function(chunk, selected_model)
            output_file.write(result + "\n")
            filtered_result = "\n".join([line for line in result.split("\n") if filter_row(line)])
            filtered_file.write(filtered_result + "\n")
            progress = int((i + 1) / total_chunks * 100)

    if not analysis_stop_event.is_set():
        progress = 100

    analysis_running = False
    analysis_stop_event.clear()
    return output_file_path


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
         Output('stop-analysis-button', 'style'),
         Output('text-content', 'children', allow_duplicate=True)],
        [Input('run-analysis-related-button', 'n_clicks'),
         Input('run-analysis-influential-button', 'n_clicks'),
         Input('run-analysis-related-concepts-button', 'n_clicks'),
         Input('stop-analysis-button', 'n_clicks'),
         Input('progress-interval', 'n_intervals')],
        [State('file-dropdown', 'value'),
         State('text-content', 'children')],
        prevent_initial_call=True
    )
    def update_progress(related_clicks, influential_clicks, related_concepts_clicks, stop_clicks, n_intervals,
                        selected_file, current_content):
        global analysis_running, progress

        ctx = callback_context
        if not ctx.triggered:
            return progress_container_style, {'width': '0%'}, "0%", True, stop_button_hidden_style, no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id in ['run-analysis-related-button', 'run-analysis-influential-button',
                          'run-analysis-related-concepts-button']:
            if not selected_file:
                return progress_container_style, {
                    'width': '0%'}, "Please select a file first.", True, stop_button_hidden_style, no_update

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

            return {'display': 'block'}, {'width': '0%'}, "0%", False, stop_button_visible_style, no_update

        elif trigger_id == 'stop-analysis-button':
            if analysis_running:
                analysis_stop_event.set()
                stop_message = f"Все ок, аналіз було на {progress}%"
                progress_bar_style = {'width': f'{progress}%', 'height': '20px', 'backgroundColor': '#ff4d4d'}
                return {
                    'display': 'block'}, progress_bar_style, stop_message, True, stop_button_hidden_style, stop_message
            else:
                return progress_container_style, {
                    'width': '0%'}, "No analysis is running.", True, stop_button_hidden_style, no_update

        elif trigger_id == 'progress-interval':
            if analysis_running:
                progress_bar_style = {'width': f'{progress}%', 'height': '20px', 'backgroundColor': '#007acc'}
                return {
                    'display': 'block'}, progress_bar_style, f"{progress}%", False, stop_button_visible_style, no_update
            else:
                if progress == 100:
                    completion_message = "Все проаналізовано"
                    progress_bar_style = {'width': '100%', 'height': '20px', 'backgroundColor': '#00cc66'}
                    return {
                        'display': 'block'}, progress_bar_style, completion_message, True, stop_button_hidden_style, completion_message
                else:
                    return progress_container_style, {'width': '0%'}, "", True, stop_button_hidden_style, no_update

        return progress_container_style, {'width': '0%'}, "", True, stop_button_hidden_style, no_update

    @app.callback(
        Output('model-selector', 'value'),
        [Input('model-selector', 'value')]
    )
    def update_model_selection(model):
        global selected_model
        selected_model = model
        return selected_model

    return app