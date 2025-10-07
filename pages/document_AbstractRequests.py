from dash import dcc, html, callback_context, no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json
from datetime import datetime
import os
import threading
import time

from components.nav import NAV_COMPONENT
from styles.document_abstrrequests_style import *
from styles.document_requests_style import radio_label_style, radio_style
from styles.style import style_alert_base, button_style, h1_style

from utils.analysing_AbstractRequests.analysis_AbstractRequests import *
from utils.documents.get_text_from_url import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEXT_DIR = os.path.join(PROJECT_ROOT, "uploads", "text")
JSON_DIR = os.path.join(PROJECT_ROOT, "processed", "json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "processed", "output")
FILTERED_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "processed", "filtered_output")

# Create directories if they don't exist
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FILTERED_OUTPUT_DIR, exist_ok=True)

# Global variables for analysis
analysis_running_abstract = False
analysis_stop_event_abstract = threading.Event()
progress_abstract = 0
selected_file_abstract = ""
selected_model = ""


def get_file_list(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except OSError as e:
        print(f"Directory access error: {e}")
        return []


def get_task_list(directory):
    try:
        if not os.path.exists(directory):
            return []
        files = [f for f in os.listdir(directory) if f.endswith('.json')]
        return sorted(files, reverse=True)
    except OSError as e:
        print(f"Task directory access error: {e}")
        return []


def load_task_data(task_filename, directory=JSON_DIR):
    try:
        file_path = os.path.join(directory, task_filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading task {task_filename}: {e}")
        return None


def create_template_prompt_content(tips_data):
    if not tips_data or not isinstance(tips_data, dict):
        return html.Div("No data to display", style={'color': 'black'})

    # Отримуємо перший елемент з масиву tips, якщо він існує
    if 'tips' in tips_data and isinstance(tips_data['tips'], list) and len(tips_data['tips']) > 0:
        tips_content = tips_data['tips'][0]
    else:
        tips_content = tips_data

    entities_of_interest = tips_content.get('entities_of_interest', [])
    relationship_types = tips_content.get('relation_types', [])
    keywords = tips_content.get('keywords', [])

    template_prompt = f'''You are an information extraction system.

Task: From the provided text, extract all relations that match the user's intent.

Entities: {entities_of_interest}  
Relation types: {relationship_types}  
Keywords: {keywords}  
'''

    return html.Div([
        html.H4("Template request:", style=left_aligned_label_style),
        html.Pre(
            template_prompt,
            style={
                'whiteSpace': 'pre-wrap',
                'wordWrap': 'break-word',
                'backgroundColor': '#fff',
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


def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"File reading error: {e}")
        return f"Error reading file: {str(e)}"


def save_relations_to_task(task_filename, relations_data, directory=JSON_DIR):
    """Зберігає зв'язки у файл завдання"""
    try:
        file_path = os.path.join(directory, task_filename)

        # Завантажуємо поточні дані завдання
        with open(file_path, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        # Оновлюємо зв'язки
        task_data["relations"] = relations_data

        # Зберігаємо оновлені дані
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Relations saved to task: {task_filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving relations: {e}")
        return False


def process_text_chunks_abstract(file_path, output_dir, tips_data, selected_model, task_filename, chunk_size=2400):
    global analysis_running_abstract, analysis_stop_event_abstract, progress_abstract
    analysis_running_abstract = True
    progress_abstract = 0

    try:
        original_filename = os.path.basename(file_path)
        output_filename = f"abstract_output_{original_filename}.txt"
        output_file_path = os.path.join(output_dir, output_filename)
        filtered_output_filename = f"filtered_abstract_{original_filename}.txt"
        filtered_output_file = os.path.join(FILTERED_OUTPUT_DIR, filtered_output_filename)

        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read().replace('\n', ' ')
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.exists(FILTERED_OUTPUT_DIR):
            os.makedirs(FILTERED_OUTPUT_DIR)

        # Отримуємо дані з правильної структури
        if 'tips' in tips_data and isinstance(tips_data['tips'], list) and len(tips_data['tips']) > 0:
            tips_content = tips_data['tips'][0]
        else:
            tips_content = tips_data

        entities_of_interest = tips_content.get('entities_of_interest', [])
        relationship_types = tips_content.get('relation_types', [])
        keywords = tips_content.get('keywords', [])

        all_relations = []  # Збираємо всі зв'язки тут

        with open(output_file_path, "w", encoding='utf-8') as output_file, open(filtered_output_file, "w",
                                                                                encoding='utf-8') as filtered_file:
            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks):
                if analysis_stop_event_abstract.is_set():
                    print(f"Analysis stopped at chunk {i + 1}/{total_chunks}")
                    break

                try:
                    result = request(chunk, entities_of_interest, relationship_types, keywords, selected_model)

                    # Записуємо результат у файли
                    output_file.write(str(result) + "\n")
                    filtered_file.write(str(result) + "\n")

                    # Додаємо зв'язки до загального списку
                    if hasattr(result, 'relations'):
                        for relation in result.relations:
                            relation_dict = {
                                "object1": relation.object1,
                                "object2": relation.object2,
                                "relation_type": relation.relation_type,
                                "polarity": relation.polarity.value,  # Конвертуємо Enum у string
                                "keywords": relation.keywords
                            }
                            all_relations.append(relation_dict)

                    progress_abstract = int((i + 1) / total_chunks * 100)
                    print(f"Processed chunk {i + 1}/{total_chunks} - Progress: {progress_abstract}%")
                    print(f"Using model: {selected_model}")

                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)

                except Exception as e:
                    print(f"Error processing chunk {i + 1}: {e}")
                    output_file.write(f"Error processing chunk: {str(e)}\n")
                    continue

        # Зберігаємо всі зв'язки у файл завдання
        if all_relations and not analysis_stop_event_abstract.is_set():
            save_relations_to_task(task_filename, all_relations)
            print(f"✅ Saved {len(all_relations)} relations to task file")

        if not analysis_stop_event_abstract.is_set():
            progress_abstract = 100
            print("Analysis completed successfully")

        analysis_running_abstract = False
        analysis_stop_event_abstract.clear()
        return output_file_path

    except Exception as e:
        print(f"Error in process_text_chunks_abstract: {e}")
        analysis_running_abstract = False
        analysis_stop_event_abstract.clear()
        return None


try:
    file_list = get_file_list(TEXT_DIR)
    task_list = get_task_list(JSON_DIR)
except Exception as e:
    print(f"List initialization error: {e}")
    file_list = []
    task_list = []

layout = html.Div(
    style=main_container_style,
    children=[
        html.H1("ConnexaData", style=h1_style),
        NAV_COMPONENT,
        dcc.Store(id='model-store', data=selected_model),
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
                            id="task-history-container",
                            style={
                                'marginTop': '20px',
                                'display': 'block'
                            },
                            children=[
                                html.Label("Previous Tasks:", style=left_aligned_label_style),
                                dcc.Dropdown(
                                    id='task-history-dropdown',
                                    options=[{'label': task.replace('.json', ''), 'value': task} for task in task_list],
                                    value=None,
                                    placeholder="Select a previous task...",
                                    style=dropdown_style
                                )
                            ]
                        ),
                        html.Div(
                            id="template-prompt",
                            children=html.Div("Your future prompt...",
                                              style={'color': '#6c757d', 'backgroundColor': '#f8f9fa'}),
                            style=future_prompt_style
                        ),
                        html.Div([
                            dcc.RadioItems(
                                id='model-selector',
                                options=[
                                    {'label': 'llama-3.3-70b-versatile (fast)', 'value': 'llama-3.3-70b-versatile'},
                                    {'label': 'qwen3:latest (slower)', 'value': 'qwen3:latest'},
                                ],
                                value=selected_model,
                                labelStyle=radio_label_style,
                                style=radio_style
                            )
                        ]),
                        html.Div(
                            id="action-buttons",
                            style=action_buttons_style,
                            children=[
                                html.Button(
                                    "Analyze",
                                    id="analyze-button",
                                    style=action_button_style_disabled,
                                    disabled=True
                                ),
                                html.Button(
                                    "Enhance",
                                    id="enhance-button",
                                    style={'display': 'none'},
                                    disabled=True
                                ),
                                html.Button(
                                    "Regenerate",
                                    id="regenerate-button",
                                    style=action_button_style_disabled,
                                    disabled=True
                                )
                            ]
                        ),

                        html.Div(
                            id='progress-container-abstract',
                            style={'display': 'none', 'marginTop': '20px'},
                            children=[
                                html.Div("Analysis Progress:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                                html.Div(
                                    style={
                                        'width': '100%',
                                        'backgroundColor': '#f0f0f0',
                                        'borderRadius': '5px',
                                        'overflow': 'hidden'
                                    },
                                    children=[
                                        html.Div(
                                            id='progress-bar-abstract',
                                            style={
                                                'width': '0%',
                                                'height': '20px',
                                                'backgroundColor': '#007acc',
                                                'transition': 'width 0.5s ease'
                                            }
                                        )
                                    ]
                                ),
                                html.Div(id='progress-text-abstract',
                                         style={'marginTop': '10px', 'textAlign': 'center'}),
                                html.Button(
                                    "Stop Analysis",
                                    id="stop-analysis-button-abstract",
                                    style={
                                        **button_style,
                                        'backgroundColor': '#dc3545',
                                        'border': 'none',
                                        'marginTop': '10px',
                                        'display': 'none'
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
        dcc.Interval(
            id='progress-interval-abstract',
            interval=1000,
            n_intervals=0,
            disabled=True
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
                    print(f"Error saving file from URL: {e}")
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
            print(f"Error creating JSON file: {e}")
            return False, str(e)

    def validate_task_inputs(task_name, task_description):
        if not task_name or not task_name.strip():
            return False, "Task name cannot be empty"

        if not task_description or not task_description.strip():
            return False, "Task description cannot be empty"

        return True, "OK"

    @app.callback(
        Output('upload-alert', 'children'),
        Output('upload-alert', 'color'),
        Output('upload-alert', 'is_open'),
        Output('task-name', 'value', allow_duplicate=True),
        Output('task-description', 'value', allow_duplicate=True),
        Output('template-prompt', 'children', allow_duplicate=True),
        Output('generate-button', 'style'),
        Output('task-history-dropdown', 'options'),
        Output('analyze-button', 'style'),
        Output('analyze-button', 'disabled'),
        Output('regenerate-button', 'style'),
        Output('regenerate-button', 'disabled'),
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
            return (validation_message, "danger", True, no_update, no_update, no_update,
                    no_update, no_update, no_update, no_update, no_update, no_update)

        try:
            success, result = create_task_json(task_name, task_description, selected_file)

            if success:
                tips_data = template_request(task_description)

                filename = os.path.basename(result)
                file_path = os.path.join("processed/json", filename)

                with open(file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)

                if hasattr(tips_data, 'model_dump'):
                    tips_dict = tips_data.model_dump()
                    task_data["tips"] = tips_dict
                else:
                    task_data["tips"] = tips_data

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)

                print("✅ Tips fields successfully filled")

                template_content = create_template_prompt_content(task_data["tips"])

                updated_task_list = get_task_list(JSON_DIR)

                button_style_hidden = button_style.copy()
                button_style_hidden['display'] = 'none'

                message = html.Div([
                    html.Span("✅ Task successfully added! ", style={'fontWeight': 'bold', 'color': 'black'}),
                    html.Br(),
                    html.Span(f"Tips generated for: {task_name}", style={'color': 'green'})
                ])
                return (message, "success", True, "", "", template_content,
                        button_style_hidden,
                        [{'label': task.replace('.json', ''), 'value': task} for task in updated_task_list],
                        action_button_style_enabled, False,
                        action_button_style_enabled, False)
            else:
                return (f"❌ Error creating template: {result}", "danger", True,
                        no_update, no_update, no_update, no_update, no_update,
                        no_update, no_update, no_update, no_update)

        except Exception as e:
            error_message = f"❌ Unexpected error: {str(e)}"
            print(f"Error: {e}")
            return (error_message, "danger", True, no_update, no_update, no_update,
                    no_update, no_update, no_update, no_update, no_update, no_update)

    @app.callback(
        Output('file-dropdown', 'options', allow_duplicate=True),
        Input('url-input', 'value'),
        prevent_initial_call=True
    )
    def update_file_list(url_value):
        if url_value and url_value.startswith(('http://', 'https://')) and '.' in url_value:
            try:
                time.sleep(0.5)
                updated_file_list = get_file_list(TEXT_DIR)
                print(f"Updated file list: {updated_file_list}")
                return [{'label': file, 'value': file} for file in updated_file_list]
            except Exception as e:
                print(f"Error updating file list: {e}")
                raise PreventUpdate

        raise PreventUpdate

    @app.callback(
        Output('task-name', 'value', allow_duplicate=True),
        Output('task-description', 'value', allow_duplicate=True),
        Output('template-prompt', 'children', allow_duplicate=True),
        Output('analyze-button', 'style', allow_duplicate=True),
        Output('analyze-button', 'disabled', allow_duplicate=True),
        Output('regenerate-button', 'style', allow_duplicate=True),
        Output('regenerate-button', 'disabled', allow_duplicate=True),
        Input('task-history-dropdown', 'value'),
        prevent_initial_call=True
    )
    def load_previous_task(selected_task):
        if not selected_task:
            raise PreventUpdate

        task_data = load_task_data(selected_task)
        if not task_data:
            return (no_update, no_update,
                    html.Div("❌ Error loading task", style={'color': 'red'}),
                    no_update, no_update, no_update, no_update)

        task_name = task_data.get('task', '')
        task_description = task_data.get('userRequest', '')

        tips = task_data.get('tips', {})
        template_content = create_template_prompt_content(tips)

        return (task_name, task_description, template_content,
                action_button_style_enabled, False,
                action_button_style_enabled, False)

    @app.callback(
        Output('upload-alert', 'children', allow_duplicate=True),
        Output('upload-alert', 'color', allow_duplicate=True),
        Output('upload-alert', 'is_open', allow_duplicate=True),
        Output('template-prompt', 'children', allow_duplicate=True),
        Input('regenerate-button', 'n_clicks'),
        State('task-name', 'value'),
        State('task-description', 'value'),
        State('file-dropdown', 'value'),
        prevent_initial_call=True
    )
    def handle_regenerate(n_clicks, task_name, task_description, selected_file):
        if not n_clicks:
            raise PreventUpdate

        try:
            success, result = create_task_json(task_name, task_description, selected_file)

            if success:
                tips_data = template_request(task_description)

                filename = os.path.basename(result)
                file_path = os.path.join("processed/json", filename)

                with open(file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)

                if hasattr(tips_data, 'model_dump'):
                    tips_dict = tips_data.model_dump()
                    task_data["tips"] = tips_dict
                else:
                    task_data["tips"] = tips_data

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)

                template_content = create_template_prompt_content(task_data["tips"])

                message = html.Div([
                    html.Span("✅ Tips successfully regenerated! ", style={'fontWeight': 'bold', 'color': 'black'}),
                    html.Br(),
                    html.Span(f"Updated for: {task_name}", style={'color': 'green'})
                ])
                return message, "success", True, template_content
            else:
                return (f"❌ Regeneration error: {result}", "danger", True, no_update)

        except Exception as e:
            error_message = f"❌ Unexpected regeneration error: {str(e)}"
            print(f"Error: {e}")
            return error_message, "danger", True, no_update

    # Callback для збереження вибраної моделі
    @app.callback(
        Output('model-store', 'data'),
        Input('model-selector', 'value')
    )
    def update_model_store(selected_model_value):
        return selected_model_value

    @app.callback(
        Output('upload-alert', 'children', allow_duplicate=True),
        Output('upload-alert', 'color', allow_duplicate=True),
        Output('upload-alert', 'is_open', allow_duplicate=True),
        Output('progress-container-abstract', 'style'),
        Output('progress-interval-abstract', 'disabled'),
        Output('stop-analysis-button-abstract', 'style'),
        Input('analyze-button', 'n_clicks'),
        State('task-name', 'value'),
        State('file-dropdown', 'value'),
        State('task-history-dropdown', 'value'),
        State('model-store', 'data'),
        prevent_initial_call=True
    )
    def handle_analyze(n_clicks, task_name, selected_file, selected_task, current_model):
        if not n_clicks:
            raise PreventUpdate

        global selected_file_abstract

        if not selected_file:
            message = html.Div([
                html.Span("❌ Please select a file first", style={'fontWeight': 'bold', 'color': 'black'})
            ])
            return message, "danger", True, no_update, no_update, no_update

        task_data = None
        task_filename = None

        if selected_task:
            task_data = load_task_data(selected_task)
            task_filename = selected_task
        else:
            task_filename = task_name.replace(" ", "_").replace("/", "_") + ".json"
            task_data = load_task_data(task_filename)

        if not task_data or 'tips' not in task_data:
            message = html.Div([
                html.Span("❌ No template found. Please generate template first.",
                          style={'fontWeight': 'bold', 'color': 'black'})
            ])
            return message, "danger", True, no_update, no_update, no_update

        selected_file_abstract = selected_file
        file_path = os.path.join(TEXT_DIR, selected_file)

        print(f"Starting analysis with model: {current_model}")
        print(f"Saving relations to task: {task_filename}")

        analysis_thread = threading.Thread(
            target=process_text_chunks_abstract,
            args=(file_path, OUTPUT_DIR, task_data['tips'], current_model, task_filename)
        )
        analysis_thread.start()

        message = html.Div([
            html.Span("🔍 Analysis started! ", style={'fontWeight': 'bold', 'color': 'black'}),
            html.Br(),
            html.Span(f"Task: {task_name}", style={'color': 'blue'}),
            html.Br(),
            html.Span(f"Model: {current_model}", style={'color': 'purple'})
        ])

        progress_container_style = {'display': 'block', 'marginTop': '20px'}
        stop_button_style = {
            **button_style,
            'backgroundColor': '#dc3545',
            'border': 'none',
            'marginTop': '10px',
            'display': 'block'
        }

        return message, "info", True, progress_container_style, False, stop_button_style

    @app.callback(
        Output('progress-bar-abstract', 'style'),
        Output('progress-text-abstract', 'children'),
        Output('progress-container-abstract', 'style', allow_duplicate=True),
        Output('stop-analysis-button-abstract', 'style', allow_duplicate=True),
        Output('progress-interval-abstract', 'disabled', allow_duplicate=True),
        Output('upload-alert', 'children', allow_duplicate=True),
        Output('upload-alert', 'color', allow_duplicate=True),
        Output('upload-alert', 'is_open', allow_duplicate=True),
        Input('progress-interval-abstract', 'n_intervals'),
        Input('stop-analysis-button-abstract', 'n_clicks'),
        prevent_initial_call=True
    )
    def update_progress_abstract(n_intervals, stop_clicks):
        global analysis_running_abstract, progress_abstract

        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        if trigger_id == 'stop-analysis-button-abstract' and stop_clicks:
            if analysis_running_abstract:
                analysis_stop_event_abstract.set()
                stop_message = html.Div([
                    html.Span("🛑 Analysis stopped! ", style={'fontWeight': 'bold', 'color': 'black'}),
                    html.Br(),
                    html.Span(f"Analysis was at {progress_abstract}%", style={'color': 'orange'})
                ])
                progress_bar_style = {
                    'width': f'{progress_abstract}%',
                    'height': '20px',
                    'backgroundColor': '#ff4d4d'
                }
                return (
                    progress_bar_style,
                    f"Stopped at {progress_abstract}%",
                    {'display': 'block', 'marginTop': '20px'},
                    {'display': 'none'},
                    True,
                    stop_message,
                    "warning",
                    True
                )

        if analysis_running_abstract:
            progress_bar_style = {
                'width': f'{progress_abstract}%',
                'height': '20px',
                'backgroundColor': '#007acc'
            }
            return (
                progress_bar_style,
                f"{progress_abstract}%",
                {'display': 'block', 'marginTop': '20px'},
                {
                    **button_style,
                    'backgroundColor': '#dc3545',
                    'border': 'none',
                    'marginTop': '10px',
                    'display': 'block'
                },
                False,
                no_update,
                no_update,
                no_update
            )
        else:
            if progress_abstract == 100:
                completion_message = html.Div([
                    html.Span("✅ Analysis completed successfully! ", style={'fontWeight': 'bold', 'color': 'black'}),
                    html.Br(),
                    html.Span("Relations saved to task file.", style={'color': 'green'})
                ])
                progress_bar_style = {
                    'width': '100%',
                    'height': '20px',
                    'backgroundColor': '#00cc66'
                }
                return (
                    progress_bar_style,
                    "100% - Completed",
                    {'display': 'block', 'marginTop': '20px'},
                    {'display': 'none'},
                    True,
                    completion_message,
                    "success",
                    True
                )
            else:
                return (
                    {'width': '0%', 'height': '20px', 'backgroundColor': '#007acc'},
                    "0%",
                    {'display': 'none'},
                    {'display': 'none'},
                    True,
                    no_update,
                    no_update,
                    no_update
                )

    return app