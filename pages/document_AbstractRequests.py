from dash import dcc, html, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import base64

# Імпортуємо ваші компоненти
from components.nav import NAV_COMPONENT
from styles.style import common_styles, h1_style, description_style, button_style, style_alert_base
from config import TEXT_FILE_PATH

def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

file_list = get_file_list(os.path.dirname(TEXT_FILE_PATH))

def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

input_style = {
    'width': '100%',
    'height': '45px',
    'border': '2px solid #ddd',
    'borderRadius': '8px',
    'padding': '0 15px',
    'fontSize': '16px',
    'marginBottom': '20px',
    'backgroundColor': '#ffffff',
    'color': '#2d3748'
}

textarea_style = {
    'width': '100%',
    'height': '120px',
    'border': '2px solid #ddd',
    'borderRadius': '8px',
    'padding': '15px',
    'fontSize': '16px',
    'marginBottom': '20px',
    'resize': 'vertical',
    'backgroundColor': '#ffffff',
    'color': '#2d3748',
    'fontFamily': 'inherit'
}

layout = html.Div(
    style={
        **common_styles,
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'backgroundColor': '#ffffff',
        'fontFamily': 'Segoe UI, system-ui, sans-serif'
    },
    children=[
        html.H1("ConnexaData", style={
            **h1_style,
            'margin': '70px 0 10px 0',
        }),
        NAV_COMPONENT,
        html.Div(
            style={
                'display': 'flex',
                'width': '90%',
                'maxWidth': '1200px',
                'height': '600px',
                'marginTop': '30px',
                'gap': '30px'
            },
            children=[
                html.Div(
                    style={
                        'flex': '1',
                        'padding': '50px',
                        'backgroundColor': '#ffffff',
                        'borderRadius': '12px',
                        'border': '1px solid #e2e8f0',
                        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'alignItems': 'center'  # Вирівнювання по центру
                    },
                    children=[
                        html.Label("Upload a file or enter a URL to start the analysis.", style={
                            'fontWeight': '600',
                            'color': '#2d3748',
                            'margin': '-10px 0 5px 0',
                            'display': 'block',
                            'fontSize': '16px',
                            'textAlign': 'left',
                            'alignSelf': 'flex-start',  # Це вирівняє лейбл по лівому краю контейнера
                            'width': '100%'  # Додайте це, щоб лейбл займав всю ширину
                        }),
                        dcc.Dropdown(
                            id='file-dropdown',
                            options=[{'label': file, 'value': file} for file in file_list],
                            value=file_list[0] if file_list else None,
                            style={'width': '100%', 'marginBottom': '8px', 'fontSize': '14px'}
                        ),
                        dcc.Upload(
                            id='upload-file',
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select Files", style={
                                    'color': '#3182ce',
                                    'textDecoration': 'underline',
                                    'fontWeight': '500'
                                })
                            ]),
                            style={
                                'width': '400px',
                                'height': '80px',
                                'lineHeight': '80px',
                                'border': '2px dashed #cbd5e0',
                                'borderRadius': '8px',
                                'textAlign': 'center',
                                'marginBottom': '20px',
                                'backgroundColor': '#f7fafc',
                                'color': '#4a5568',
                                'fontSize': '16px'
                            },
                            multiple=False,
                            accept='.txt,.pdf,.docx',
                            max_size=5 * 1024 * 1024
                        ),
                        html.Label("Or", style={
                            'fontWeight': '600',
                            'color': '#2d3748',
                            'margin': '-10px 0 5px 0',
                            'display': 'block',
                            'fontSize': '16px'
                        }),
                        dcc.Input(
                            id='url-input',
                            type='url',
                            placeholder='Enter URL',
                            style=input_style
                        ),
                        dbc.Alert(
                            id='upload-alert',
                            color="danger",
                            is_open=False,
                            duration=4000,
                            style=style_alert_base
                        ),
                        html.Label("Enter the task name", style={
                            'fontWeight': '600',
                            'color': '#2d3748',
                            'margin': '-10px 0 5px 0',
                            'display': 'block',
                            'fontSize': '16px',
                            'textAlign': 'left',
                            'alignSelf': 'flex-start',  # Це вирівняє лейбл по лівому краю контейнера
                            'width': '100%'  # Додайте це, щоб лейбл займав всю ширину
                        }),
                        dcc.Input(
                            id='task-name',
                            type='text',
                            placeholder='Task Name',
                            style=input_style
                        ),
                        dcc.Textarea(
                            id='task-description',
                            placeholder='Enter task description',
                            style=textarea_style
                        ),
                        html.Button(
                            "Generate",
                            id="generate-button",
                            style={
                                **button_style,
                                'border': 'none',
                                'width': '150px',
                                'padding': '15px',
                                'fontSize': '18px',
                                'fontWeight': '600',
                                'borderRadius': '8px',
                                'cursor': 'pointer',
                                'marginTop': 'auto'
                            }
                        )
                    ]
                ),
                html.Div(
                    style={
                        'flex': '1',
                        'padding': '30px',
                        'backgroundColor': '#ffffff',
                        'borderRadius': '12px',
                        'border': '1px solid #e2e8f0',
                        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                        'overflowY': 'auto',
                        'textAlign': 'left'  # Вирівнювання тексту по лівій стороні
                    },
                    children=[
                        html.H3("Document Content", style={
                            'marginBottom': '20px',
                            'color': '#2d3748',
                            'fontSize': '20px',
                            'fontWeight': '600',
                            'textAlign': 'left'  # Вирівнювання заголовка по лівій стороні
                        }),
                        html.Div(
                            id='document-content',
                            style={
                                'lineHeight': '1.6',
                                'color': '#4a5568',
                                'fontSize': '16px',
                                'whiteSpace': 'pre-wrap',
                                'textAlign': 'left'  # Вирівнювання контенту по лівій стороні
                            }
                        ),
                        html.Div(
                            id='upload-error',
                            style={'display': 'none'}
                        )
                    ]
                )
            ]
        )
    ]
)

def register_callbacks(app):
    # Callback для завантаження файлів
    @app.callback(
        Output('file-dropdown', 'options', allow_duplicate=True),
        Output('file-dropdown', 'value', allow_duplicate=True),
        Output('upload-alert', 'children'),
        Output('upload-alert', 'is_open'),
        Input('upload-file', 'contents'),
        State('upload-file', 'filename'),
        State('upload-file', 'last_modified'),
        prevent_initial_call=True
    )
    def upload_file(contents, filename, last_modified):
        if contents is None:
            raise PreventUpdate
        try:
            upload_dir = os.path.dirname(TEXT_FILE_PATH)
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded)
            new_file_list = get_file_list(upload_dir)
            return ([{'label': file, 'value': file} for file in new_file_list],
                    filename,
                    f"File {filename} uploaded successfully!",
                    True)
        except Exception as e:
            return (no_update,
                    no_update,
                    f"Error uploading file: {str(e)}",
                    True)

    @app.callback(
        Output('document-content', 'children'),
        Input('file-dropdown', 'value')
    )
    def display_selected_file_content(selected_file):
        if not selected_file:
            return "Select or upload a document to view its content here."
        try:
            file_path = os.path.join(os.path.dirname(TEXT_FILE_PATH), selected_file)
            content = read_text_file(file_path)
            word_count = len(content.split())
            char_count = len(content)
            file_info = html.Div([
                html.Hr(),
                html.P(f"File: {selected_file} | Words: {word_count} | Characters: {char_count}",
                       style={'fontSize': '14px', 'color': '#718096', 'marginTop': '10px', 'textAlign': 'left'})
            ])
            return [html.Div(content, style={'whiteSpace': 'pre-wrap', 'textAlign': 'left'}), file_info]
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @app.callback(
        Output('upload-alert', 'children', allow_duplicate=True),
        Output('upload-alert', 'is_open', allow_duplicate=True),
        Input('url-input', 'value'),
        prevent_initial_call=True
    )
    def handle_url(url):
        if not url:
            raise PreventUpdate
        if url.startswith(('http://', 'https://')):
            return f"URL {url} submitted successfully!", True
        return "Error: Invalid URL format.", True

    @app.callback(
        Output('generate-button', 'children'),
        Input('generate-button', 'n_clicks'),
        State('task-name', 'value'),
        State('task-description', 'value'),
        State('file-dropdown', 'value'),
        State('upload-file', 'contents'),
        State('url-input', 'value'),
        prevent_initial_call=True
    )
    def handle_generate(n_clicks, task_name, task_description, selected_file, file_contents, url):
        if n_clicks is None:
            return no_update
        if not task_name or not task_description:
            return "Please fill in all required fields."
        if not selected_file and not file_contents and not url:
            return "Please select a file, upload a file, or enter a URL."
        return "Generated!"

    return app