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
                        html.Button(
                            "Generate Template",
                            id="generate-button",
                            style=button_style
                        ),
                        html.Div(
                            id="template-prompt",
                            children="Your future prompt...",
                            style={**future_prompt_style, 'color': '#6c757d', 'backgroundColor': '#f8f9fa'}
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
                            style={**document_content_style, 'maxHeight': '600px', 'overflowY': 'auto'},
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
                    saved_filename = save_to_file(result, url_value, TEXT_DIR)
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

    def create_task_json(task_title, userRequest, selected_file=None, output_dir="processed/json"):
        try:
            os.makedirs(output_dir, exist_ok=True)

            safe_filename = task_title.replace(" ", "_").replace("/", "_") + ".json"
            file_path = os.path.join(output_dir, safe_filename)

            task_data = {
                "task": task_title,
                "userRequest": userRequest,
                "files": [selected_file] if selected_file else [],
                "tips": "",
                "relations": [],
                "created_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)

            return True, file_path
        except Exception as e:
            print(f"Помилка при створенні JSON файлу: {e}")
            return False, str(e)

    def validate_task_inputs(task_name, task_description):
        if not task_name or not task_name.strip():
            return False, "Назва таску не може бути порожньою"

        if not task_description or not task_description.strip():
            return False, "Опис таску не може бути порожнім"

        return True, "OK"

    @app.callback(
        Output('upload-alert', 'children'),
        Output('upload-alert', 'color'),
        Output('upload-alert', 'is_open'),
        Output('task-name', 'value'),
        Output('task-description', 'value'),
        Output('template-prompt', 'children'),
        Input('generate-button', 'n_clicks'),
        State('task-name', 'value'),
        State('task-description', 'value'),
        State('file-dropdown', 'value'),
        prevent_initial_call=True
    )
    def handle_generate_template(n_clicks, task_name, task_description, selected_file):
        if not n_clicks:
            raise PreventUpdate

        is_valid, validation_message = validate_task_inputs(task_name, task_description)
        if not is_valid:
            return validation_message, "danger", True, no_update, no_update, no_update

        try:
            success, result = create_task_json(task_name, task_description, selected_file)

            if success:
                # одразу додає tips_data замість Tips
                tips_data = template_request(task_description)

                filename = os.path.basename(result)
                file_path = os.path.join("processed/json", filename)

                with open(file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)

                if hasattr(tips_data, 'model_dump'):
                    tips_dict = tips_data.model_dump()
                    # Беремо перший елемент списка tips, якщо він є
                    task_data["tips"] = tips_dict.get("tips", [{}])[0] if tips_dict.get("tips") else {}
                else:
                    # Аналогічно для словника
                    task_data["tips"] = tips_data.get("tips", [{}])[0] if tips_data.get("tips") else {}

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)

                print("✅ Поля Tips успішно заповнено:")

                # Створюємо контент для шаблонного промпту
                template_content = []

                # Отримуємо перший елемент з масиву tips для відображення
                if task_data["tips"] and isinstance(task_data["tips"], dict):
                    tip = task_data["tips"]

                    # Отримуємо значення для підстановки
                    entities_of_interest = tip.get('entities_of_interest', [])
                    relationship_types = tip.get('relation_types', [])
                    keywords = tip.get('keywords', [])

                    # Формуємо шаблонний промпт
                    template_prompt = f'''You are an information extraction system.

                Task: From the provided text, extract all relations that match the user's intent.

                Entities: {entities_of_interest}  
                Relation types: {relationship_types}  
                Keywords: {keywords}  

                Output JSON fields:  
                object1, object2, relation_type, polarity, keywords'''

                    # Додаємо шаблонний промпт в інтерфейс
                    template_content = html.Div([
                        html.H4("Шаблонний промпт:", style={'marginBottom': '10px', 'color': 'black'}),
                        html.Pre(
                            template_prompt,
                            style={
                                'whiteSpace': 'pre-wrap',
                                'wordWrap': 'break-word',
                                'backgroundColor': '#f8f9fa',
                                'padding': '15px',
                                'borderRadius': '5px',
                                'border': '1px solid #dee2e6',
                                'color': 'black',
                                'fontFamily': 'monospace',
                                'fontSize': '14px',
                                'lineHeight': '1.4',
                                'maxHeight': '400px',
                                'overflowY': 'auto'
                            }
                        )
                    ])

                    # Вивід в консоль для дебагу
                    print(f"   Entities of interest: {entities_of_interest}")
                    print(f"   Relationship types: {relationship_types}")
                    print(f"   Keywords: {keywords}")
                    print(f"   File name: {selected_file}")
                else:
                    template_content = html.Div("Немає даних для відображення", style={'color': 'black'})
                    print("   Немає даних для відображення")

                message = html.Div([
                    html.Span("✅ Завдання успішно додано! ", style={'fontWeight': 'bold', 'color': 'black'}),
                    html.Br(),
                    html.Span(f"Tips заповнено для: {task_name}", style={'color': 'green'})
                ])
                return message, "success", True, "", "", template_content
            else:
                return f"❌ Помилка при створенні шаблону: {result}", "danger", True, no_update, no_update, no_update

        except Exception as e:
            error_message = f"❌ Неочікувана помилка: {str(e)}"
            print(f"Помилка: {e}")
            return error_message, "danger", True, no_update, no_update, no_update

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