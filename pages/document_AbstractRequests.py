from dash import dcc, html, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import json
from datetime import datetime
import threading
import os

from components.nav import NAV_COMPONENT
from styles.document_abstrrequests_style import *
from styles.style import style_alert_base, button_style, h1_style

from utils.analysing_AbstractRequests.analysis_AbstractRequests import *
from utils.documents.get_text_from_url import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEXT_DIR = os.path.join(PROJECT_ROOT, "uploads", "text")
model = "qwen3:latest"


def get_file_list(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except OSError as e:
        print(f"Помилка доступу до директорії: {e}")
        return []


try:
    file_list = get_file_list(TEXT_DIR)
except Exception as e:
    print(f"Помилка ініціалізації file_list: {e}")
    file_list = []


def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        return f"Error reading file: {str(e)}"


layout = html.Div(
    style=main_container_style,
    children=[
        html.H1("ConnexaData", style=h1_style),
        NAV_COMPONENT,
        html.Div(
            style=content_wrapper_style,
            children=[
                html.Div(
                    style=input_panel_style,
                    children=[
                        html.Label("Upload a file or enter a URL to start the analysis.",
                                   style=left_aligned_label_style),
                        dcc.Dropdown(
                            id='file-dropdown',
                            options=[{'label': file, 'value': file} for file in file_list],
                            value=None,
                            style=dropdown_style
                        ),
                        dcc.Upload(
                            id='upload-file',
                            children=html.Div([
                                "Drag and Drop or ",
                                html.A("Select Files", style=link_style)
                            ]),
                            style=upload_area_style,
                            multiple=False,
                            accept='.txt,.pdf,.docx',
                            max_size=5 * 1024 * 1024
                        ),
                        html.Label("Or", style={**label_style, 'textAlign': 'center', 'fontStyle': 'italic'}),
                        dcc.Input(
                            id='url-input',
                            type='url',
                            placeholder='Enter URL here...',
                            style=input_field_style
                        ),
                        dbc.Alert(
                            id='upload-alert',
                            color="danger",
                            is_open=False,
                            duration=4000,
                            style=style_alert_base
                        ),
                        html.Label("Enter the task name", style=left_aligned_label_style),
                        dcc.Input(
                            id='task-name',
                            type='text',
                            placeholder='Task Name',
                            style=input_field_style
                        ),
                        html.Label("Task Description", style=left_aligned_label_style),
                        dcc.Textarea(
                            id='task-description',
                            placeholder='Enter task description...',
                            style=text_area_style
                        ),
                        html.Div(
                            id='abstract-progress-container',
                            style={
                                'display': 'none',
                                'marginTop': '15px',
                                'marginBottom': '15px'
                            },
                            children=[
                                html.Div(
                                    id='abstract-progress-text',
                                    children="0%",
                                    style={
                                        'textAlign': 'center',
                                        'marginBottom': '5px',
                                        'fontWeight': 'bold',
                                        'color': colors['primary']
                                    }
                                ),
                                html.Div(
                                    id='abstract-progress-bar-placeholder',
                                    style=progress_bar_placeholder_style,
                                    children=[
                                        html.Div(
                                            id='abstract-progress-bar',
                                            style={
                                                'height': '100%',
                                                'borderRadius': '4px',
                                                'width': '0%',
                                                'transition': 'width 0.8s ease',
                                                'backgroundColor': colors['primary']
                                            }
                                        )
                                    ]
                                ),
                                html.Button(
                                    "Stop Analysis",
                                    id="abstract-stop-analysis-button",
                                    style={
                                        'display': 'none',
                                        'backgroundColor': '#dc3545',
                                        'color': 'white',
                                        'border': 'none',
                                        'padding': '10px 20px',
                                        'borderRadius': '5px',
                                        'cursor': 'pointer',
                                        'marginTop': '10px',
                                        'width': '100%'
                                    }
                                )
                            ]
                        ),
                        html.Button(
                            "Generate Template",
                            id="generate-button",
                            style=button_style
                        ),
                        html.Div(
                            id='template-prompt-container',
                            style={
                                'display': 'none',
                                'marginTop': '20px',
                                'padding': '15px',
                                'backgroundColor': '#f8f9fa',
                                'borderRadius': '8px',
                                'border': '1px solid #dee2e6'
                            },
                            children=[
                                html.H5("Шаблонний промпт",
                                        style={'color': colors['dark_text'], 'marginBottom': '10px'}),
                                html.Div(id='template-prompt-content', style={'whiteSpace': 'pre-wrap'}),
                                html.Div(
                                    style={
                                        'display': 'flex',
                                        'justifyContent': 'space-between',
                                        'marginTop': '15px',
                                        'gap': '10px'
                                    },
                                    children=[
                                        html.Button("Так, продовжити", id="yes-button", style={
                                            'backgroundColor': '#28a745',
                                            'color': 'white',
                                            'border': 'none',
                                            'padding': '10px 20px',
                                            'borderRadius': '5px',
                                            'cursor': 'pointer',
                                            'flex': '1'
                                        }),
                                        html.Button("Доповнити (у розробці)", id="expand-button", style={
                                            'backgroundColor': '#ffc107',
                                            'color': 'black',
                                            'border': 'none',
                                            'padding': '10px 20px',
                                            'borderRadius': '5px',
                                            'cursor': 'not-allowed',
                                            'flex': '1'
                                        }),
                                        html.Button("Ні, згенерувати знову", id="no-button", style={
                                            'backgroundColor': '#dc3545',
                                            'color': 'white',
                                            'border': 'none',
                                            'padding': '10px 20px',
                                            'borderRadius': '5px',
                                            'cursor': 'pointer',
                                            'flex': '1'
                                        })
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id='analysis-result-container',
                            style={'display': 'none', 'marginTop': '25px'},
                            children=[
                                html.H4("Результати аналізу",
                                        style={'color': colors['dark_text'], 'marginBottom': '15px',
                                               'textAlign': 'center'}),
                                html.Div(
                                    id='analysis-result-content',
                                    style={
                                        'backgroundColor': '#ffffff',
                                        'border': '1px solid #dee2e6',
                                        'borderRadius': '8px',
                                        'padding': '20px',
                                        'maxHeight': '400px',
                                        'overflowY': 'auto',
                                        'marginBottom': '15px'
                                    }
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    style=output_panel_style,
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'marginBottom': '15px',
                                'flexWrap': 'wrap',
                                'gap': '10px'
                            },
                            children=[
                                html.H3("Document Content", style=document_title_style),
                                html.Div(
                                    id='file-info-container',
                                    style=file_info_container_style,
                                    children="No file selected"
                                )
                            ]
                        ),
                        html.Div(
                            id='document-content',
                            style=document_content_style,
                            children="Select or upload a document to view its content here..."
                        ),
                        html.Div(
                            id='upload-error',
                            style={'display': 'none'}
                        )
                    ]
                )
            ]
        ),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output('document-content', 'children'),
        Output('file-info-container', 'children'),
        Output('url-input', 'style'),
        Input('file-dropdown', 'value'),
        Input('url-input', 'value'),
        prevent_initial_call=True
    )
    def handle_file_and_url_updates(selected_file, url_value):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        if triggered_id == 'file-dropdown' and selected_file:
            try:
                file_path = os.path.join(TEXT_DIR, selected_file)
                content = read_text_file(file_path)

                word_count = len(content.split())
                character_count = len(content)

                truncated_filename = selected_file
                if len(selected_file) > 30:
                    truncated_filename = selected_file[:27] + "..."

                file_info = html.Div([
                    html.Div(f"📄 {truncated_filename}", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    html.Div(f"📝 {word_count} words | 🔤 {character_count} chars",
                             style={'fontSize': '12px', 'color': colors['gray_text']})
                ])

                return content, file_info, input_field_style

            except Exception as error:
                error_message = f"Error reading file: {str(error)}"
                return error_message, html.Div("❌ Error loading file",
                                               style={'color': colors['danger']}), input_field_style

        elif triggered_id == 'url-input' and url_value:
            url_style = input_field_style.copy()

            if url_value.startswith(('http://', 'https://')) and '.' in url_value:
                url_style['border'] = '2px solid green'
                url_style['backgroundColor'] = '#f0fff0'

                try:
                    result = extract_text_in_order(url_value)
                    save_to_file(result, url_value, TEXT_DIR)
                    return no_update, no_update, url_style

                except Exception as e:
                    print(f"Помилка при збереженні файлу з URL: {e}")
                    url_style['border'] = '2px solid red'
                    url_style['backgroundColor'] = '#fff0f0'
                    return no_update, no_update, url_style
            else:
                url_style['border'] = '2px solid red'
                url_style['backgroundColor'] = '#fff0f0'
                return no_update, no_update, url_style

        raise PreventUpdate

    @app.callback(
        Output('file-dropdown', 'options', allow_duplicate=True),
        Input('url-input', 'value'),
        prevent_initial_call=True
    )
    def update_file_list(url_value):
        if url_value and url_value.startswith(('http://', 'https://')) and '.' in url_value:
            try:
                import time
                time.sleep(0.5)

                updated_file_list = get_file_list(TEXT_DIR)
                print(f"Оновлений список файлів: {updated_file_list}")
                return [{'label': file, 'value': file} for file in updated_file_list]
            except Exception as e:
                print(f"Помилка при оновленні списку файлів: {e}")
                raise PreventUpdate

        raise PreventUpdate

    return app