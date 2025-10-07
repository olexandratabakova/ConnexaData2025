from dash import dcc, Input, Output, State, html, callback_context
import dash_cytoscape as cyto
from styles.style import (
    visualization_layout_style,
    visualization_cytoscape_style,
    button_style,
    button_style_backtohome,
    sidebar_style,
    main_content_style
)
import dash_daq as daq
from dash.exceptions import PreventUpdate
import os

from components.dropdown import create_dropdown
from components.node_panels import create_rename_panel
from utils.viz.nodes import *
from components.nav import NAV_COMPONENT

# Fixed path constants - same approach as in working code
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
JSON_DIR = os.path.join(PROJECT_ROOT, "processed", "json")

# Styles for panels
PANEL_STYLE = {
    'background': 'white',
    'padding': '15px',
    'borderRadius': '8px',
    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
    'maxWidth': '300px',
    'zIndex': 1000,
    'fontFamily': 'Helvetica',
    'fontSize': '13px',
    'border': '1px solid #e1e1e1'
}

PANEL_HEADER_STYLE = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'alignItems': 'center',
    'marginBottom': '10px',
    'paddingBottom': '10px',
    'borderBottom': '1px solid #e1e1e1'
}

PANEL_TITLE_STYLE = {
    'color': '#1B5E67',
    'fontWeight': 'bold',
    'fontSize': '14px',
    'margin': 0
}

CLOSE_BUTTON_STYLE = {
    'background': 'none',
    'border': 'none',
    'fontSize': '16px',
    'cursor': 'pointer',
    'color': '#666',
    'padding': '0',
    'width': '20px',
    'height': '20px',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center'
}

PANEL_CONTENT_STYLE = {
    'color': '#333',
    'lineHeight': '1.4'
}

# Оновлений стиль для бічної панелі - ширша, з вертикальним скролом
UPDATED_SIDEBAR_STYLE = {
    'width': '400px',  # Ще трохи ширше
    'padding': '20px',
    'backgroundColor': 'white',
    'borderRight': '1px solid #e1e1e1',
    'height': 'calc(100vh - 60px)',  # Більше місця для контенту
    'marginTop': '60px',
    'overflowY': 'auto',  # Вертикальний скрол
    'overflowX': 'hidden',
    'fontFamily': 'Helvetica',
    'position': 'fixed',
    'left': 0,
    'top': 0
}

# Оновлений стиль для основного контенту
UPDATED_MAIN_CONTENT_STYLE = {
    'flex': '1',
    'padding': '20px',
    'marginLeft': '400px',
    'backgroundColor': 'white',
    'height': '100vh',
    'overflow': 'auto',
    'fontFamily': 'Helvetica',
    'minWidth': '600px'
}


def create_layout(file_path, min_color, max_color, max_objects, avg_size, node_spacing):
    nodes, edges, error_message = load_data(file_path, min_color, max_color, max_objects, avg_size)
    if error_message:
        return html.Div(
            error_message,
            style={
                'color': '#333333',
                'textAlign': 'center',
                'fontSize': '16px',
                'padding': '20px',
                'fontFamily': 'Helvetica'
            }
        )

    return html.Div(
        style=visualization_layout_style,
        children=[
            cyto.Cytoscape(
                id='cytoscape-graph',
                elements=nodes + edges,
                layout={'name': 'preset', 'spacingFactor': node_spacing / 100},
                style=visualization_cytoscape_style,
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'content': 'data(label)',
                            'background-color': 'data(color)',
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'border-color': 'data(border_color)',
                            'border-width': '2px',
                            'text-halign': 'center',
                            'text-valign': 'center',
                            'font-family': 'Helvetica'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'line-color': 'data(color)',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': 'data(color)',
                            'font-family': 'Helvetica'
                        }
                    }
                ]
            ),
            html.Div(
                id='panels-container',
                style={
                    'position': 'fixed',
                    'bottom': '20px',
                    'left': '50%',
                    'transform': 'translateX(-50%)',
                    'display': 'flex',
                    'gap': '15px',
                    'zIndex': 1000,
                    'maxWidth': '90%',
                    'flexWrap': 'wrap',
                    'justifyContent': 'center'
                },
                children=[
                    html.Div(
                        id='node-panel',
                        style={**PANEL_STYLE, 'display': 'none'},
                        children=[
                            html.Div(
                                style=PANEL_HEADER_STYLE,
                                children=[
                                    html.H4("Node Information", style=PANEL_TITLE_STYLE),
                                    html.Button(
                                        "×",
                                        id='close-node-panel',
                                        style=CLOSE_BUTTON_STYLE,
                                        title="Close"
                                    )
                                ]
                            ),
                            html.Div(id='node-panel-content', style=PANEL_CONTENT_STYLE)
                        ]
                    ),
                    html.Div(
                        id='edge-panel',
                        style={**PANEL_STYLE, 'display': 'none'},
                        children=[
                            html.Div(
                                style=PANEL_HEADER_STYLE,
                                children=[
                                    html.H4("Edge Information", style=PANEL_TITLE_STYLE),
                                    html.Button(
                                        "×",
                                        id='close-edge-panel',
                                        style=CLOSE_BUTTON_STYLE,
                                        title="Close"
                                    )
                                ]
                            ),
                            html.Div(id='edge-panel-content', style=PANEL_CONTENT_STYLE)
                        ]
                    )
                ]
            )
        ]
    )


def get_json_files():
    """Get list of JSON files from directory"""
    try:
        if os.path.exists(JSON_DIR):
            json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
            return [{'label': file, 'value': os.path.join(JSON_DIR, file)} for file in json_files]
        else:
            print(f"Directory {JSON_DIR} does not exist")
            return []
    except Exception as e:
        print(f"Error getting JSON files: {e}")
        return []


layout = html.Div(
    style={
        'display': 'flex',
        'flexDirection': 'row',
        'height': '100vh',
        'fontFamily': 'Helvetica',
        'backgroundColor': 'white',
    },
    children=[
        NAV_COMPONENT,
        dcc.Download(id="download-csv"),
        html.Div(
            id='sidebar',
            style=UPDATED_SIDEBAR_STYLE,
            children=[
                html.H3("Visualization", style={
                    'color': '#1B5E67',
                    'fontFamily': 'Helvetica',
                    'marginBottom': '20px',
                    'textAlign': 'center',
                    'fontSize': '20px',
                    'fontWeight': '600'
                }),

                # JSON file dropdown
                html.Div([
                    html.Label("JSON File", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Dropdown(
                        id='json-file-dropdown',
                        options=get_json_files(),
                        placeholder="Select JSON file",
                        style={
                            'width': '100%',
                            'marginBottom': '20px',
                            'fontFamily': 'Helvetica',
                            'color': '#333333'
                        },
                        clearable=False,
                    ),
                ]),

                # Layout dropdown
                html.Div([
                    html.Label("Layout Preset", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Dropdown(
                        id='layout-dropdown',
                        options=[
                            {'label': 'Random', 'value': 'random'},
                            {'label': 'Preset', 'value': 'preset'},
                            {'label': 'Grid', 'value': 'grid'},
                            {'label': 'Circle', 'value': 'circle'},
                            {'label': 'Concentric', 'value': 'concentric'},
                            {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                            {'label': 'Cose', 'value': 'cose'}
                        ],
                        placeholder="Select a preset",
                        style={
                            'width': '100%',
                            'marginBottom': '20px',
                            'fontFamily': 'Helvetica',
                            'color': '#333333'
                        },
                        clearable=False,
                    ),
                ]),

                # Show Edge Labels Toggle
                html.Div([
                    html.Label("Show Edge Labels", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    daq.BooleanSwitch(
                        id='edge-labels-toggle',
                        on=False,
                        color='#1B5E67',
                        style={
                            'marginBottom': '20px'
                        }
                    ),
                ]),

                html.H3("Size Settings", style={
                    'color': '#1B5E67',
                    'fontFamily': 'Helvetica',
                    'marginBottom': '15px',
                    'textAlign': 'center',
                    'fontSize': '18px',
                    'fontWeight': '600'
                }),

                # Text Size
                html.Div([
                    html.Label("Text Size", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='text-size-slider',
                        min=10,
                        max=30,
                        step=1,
                        value=12,
                        marks={i: str(i) for i in range(10, 31, 5)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '20px'}),

                # Node Size
                html.Div([
                    html.Label("Node Size", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='node-size-slider',
                        min=10,
                        max=150,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 151, 20)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '20px'}),

                # Edge Thickness
                html.Div([
                    html.Label("Edge Thickness", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='edge-thickness-slider',
                        min=1,
                        max=10,
                        step=1,
                        value=2,
                        marks={i: str(i) for i in range(1, 11, 1)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '20px'}),

                # Node Spacing
                html.Div([
                    html.Label("Node Spacing", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='node-spacing-slider',
                        min=100,
                        max=5000,
                        step=50,
                        value=100,
                        marks={i: str(i) for i in range(100, 5000, 500)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '20px'}),

                # Average Node Size
                html.Div([
                    html.Label("Average Node Size", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='avg-size-slider',
                        min=10,
                        max=100,
                        step=5,
                        value=30,
                        marks={i: str(i) for i in range(10, 101, 10)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '20px'}),

                html.H3("Colors", style={
                    'color': '#1B5E67',
                    'fontFamily': 'Helvetica',
                    'marginBottom': '15px',
                    'textAlign': 'center',
                    'fontSize': '18px',
                    'fontWeight': '600'
                }),

                # Color Pickers - розташовані окремо один під одним
                html.Div([
                    html.Label("Min Color", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'marginBottom': '10px',
                        'fontWeight': '500',
                        'fontSize': '14px',
                        'textAlign': 'center',
                        'width': '100%'
                    }),
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginBottom': '25px',
                            'width': '100%'
                        },
                        children=[
                            daq.ColorPicker(
                                id='min-color-picker',
                                value=dict(hex='#FF69B4'),
                                style={
                                    'border': 'none',
                                    'boxShadow': 'none',
                                    'width': '100%',
                                    'maxWidth': '200px'
                                }
                            )
                        ]
                    )
                ]),

                html.Div([
                    html.Label("Max Color", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'marginBottom': '10px',
                        'fontWeight': '500',
                        'fontSize': '14px',
                        'textAlign': 'center',
                        'width': '100%'
                    }),
                    html.Div(
                        style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'marginBottom': '25px',
                            'width': '100%'
                        },
                        children=[
                            daq.ColorPicker(
                                id='max-color-picker',
                                value=dict(hex='#1E90FF'),
                                style={
                                    'border': 'none',
                                    'boxShadow': 'none',
                                    'width': '100%',
                                    'maxWidth': '200px'
                                }
                            )
                        ]
                    )
                ]),

                # Max Objects
                html.Div([
                    html.Label("Max Objects", style={
                        'color': '#1B5E67',
                        'fontFamily': 'Helvetica',
                        'textAlign': 'left',
                        'marginBottom': '8px',
                        'fontWeight': '500',
                        'fontSize': '14px'
                    }),
                    dcc.Slider(
                        id='max-objects-slider',
                        min=10,
                        max=500,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 501, 50)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                ], style={'width': '100%', 'marginBottom': '30px'}),

                # Apply Button - тепер видно в кінці
                html.Div([
                    html.Button("Apply Settings", id='apply-button', style={
                        **button_style,
                        'margin': '50px auto',
                        'display': 'block'
                    })], style={'width': '100%'})
            ]
        ),

        html.Div(
            id='main-content',
            style=UPDATED_MAIN_CONTENT_STYLE,
            children=[
                html.Div(id='visualization-content')
            ]
        )
    ]
)


def register_callbacks(app):
    @app.callback(
        Output('visualization-content', 'children'),
        Input('apply-button', 'n_clicks'),
        State('json-file-dropdown', 'value'),
        State('min-color-picker', 'value'),
        State('max-color-picker', 'value'),
        State('max-objects-slider', 'value'),
        State('avg-size-slider', 'value'),
        State('node-spacing-slider', 'value')
    )
    def update_visualization(n_clicks, json_file, min_color, max_color, max_objects, avg_size, node_spacing):
        if n_clicks is None or not json_file:
            return html.Div([
                html.Div("Please select a JSON file and click 'Apply Settings' to visualize.",
                         style={
                             'color': '#333333',
                             'textAlign': 'center',
                             'fontSize': '16px',
                             'fontFamily': 'Helvetica'
                         }),
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'alignItems': 'center',
                'height': '100vh'
            })

        return create_layout(json_file, min_color['hex'], max_color['hex'], max_objects, avg_size, node_spacing)

    @app.callback(
        Output('cytoscape-graph', 'stylesheet'),
        Input('apply-button', 'n_clicks'),
        State('text-size-slider', 'value'),
        State('node-size-slider', 'value'),
        State('edge-thickness-slider', 'value'),
        State('edge-labels-toggle', 'on')
    )
    def update_stylesheet(n_clicks, text_size, node_size, edge_thickness, show_edge_labels):
        if n_clicks is None:
            return []

        stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'font-size': f"{text_size}px",
                    'background-color': 'data(color)',
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'border-color': 'data(border_color)',
                    'border-width': '2px',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    'font-family': 'Helvetica'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': 'data(color)',
                    'width': f'{edge_thickness}',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': 'data(color)',
                    'font-family': 'Helvetica'
                }
            }
        ]

        # Додаємо стиль для відображення міток на ребрах, якщо перемикач увімкнено
        if show_edge_labels:
            stylesheet.append({
                'selector': 'edge',
                'style': {
                    'label': 'data(relation_type)',
                    'text-rotation': 'autorotate',
                    'text-margin-x': '0px',
                    'text-margin-y': '0px',
                    'font-size': f'{max(8, text_size - 2)}px',
                    'color': '#333333',
                    'text-outline-color': '#ffffff',
                    'text-outline-width': '2px',
                    'text-outline-opacity': 0.8
                }
            })

        return stylesheet

    @app.callback(
        Output('cytoscape-graph', 'layout'),
        Input('layout-dropdown', 'value')
    )
    def update_layout(selected_layout):
        if selected_layout is None:
            return {'name': 'preset'}
        return {'name': selected_layout}

    @app.callback(
        Output('node-panel-content', 'children'),
        Output('node-panel', 'style'),
        Input('cytoscape-graph', 'tapNodeData'),
    )
    def update_node_panel_content(node_data):
        if not node_data:
            return [], {**PANEL_STYLE, 'display': 'none'}

        merged_parts = node_data.get('merged_parts', [])
        if not merged_parts:
            return [], {**PANEL_STYLE, 'display': 'none'}

        current_label = node_data.get('label', merged_parts[0])
        content = create_rename_panel(merged_parts, current_label)

        return content, {**PANEL_STYLE, 'display': 'block'}

    @app.callback(
        Output('edge-panel-content', 'children'),
        Output('edge-panel', 'style'),
        Input('cytoscape-graph', 'tapEdgeData'),
    )
    def update_edge_panel_content(edge_data):
        if not edge_data:
            return [], {**PANEL_STYLE, 'display': 'none'}

        content = html.Div([
            html.P(f"Object 1: {edge_data.get('source', '')}", style={'margin': '5px 0'}),
            html.P(f"Object 2: {edge_data.get('target', '')}", style={'margin': '5px 0'}),
            html.P(f"Relation type: {edge_data.get('relation_type', '')}", style={'margin': '5px 0'}),
            html.P(f"Polarity: {edge_data.get('polarity', '')}", style={'margin': '5px 0'}),
            html.P(f"Keywords: {', '.join(edge_data.get('keywords', []))}", style={'margin': '5px 0'}),
        ])

        return content, {**PANEL_STYLE, 'display': 'block'}

    @app.callback(
        Output('node-panel', 'style', allow_duplicate=True),
        Input('close-node-panel', 'n_clicks'),
        prevent_initial_call=True
    )
    def close_node_panel(n_clicks):
        return {**PANEL_STYLE, 'display': 'none'}

    @app.callback(
        Output('edge-panel', 'style', allow_duplicate=True),
        Input('close-edge-panel', 'n_clicks'),
        prevent_initial_call=True
    )
    def close_edge_panel(n_clicks):
        return {**PANEL_STYLE, 'display': 'none'}

    @app.callback(
        Output('cytoscape-graph', 'elements'),
        Input('label-radio', 'value'),
        State('cytoscape-graph', 'elements'),
        State('cytoscape-graph', 'tapNodeData'),
        prevent_initial_call=True
    )
    def update_node_label(selected_label, elements, node_data):
        if not node_data:
            raise PreventUpdate

        updated_elements = []
        for element in elements:
            if 'data' in element and element['data'].get('id') == node_data.get('id'):
                element['data']['label'] = selected_label
            updated_elements.append(element)

        return updated_elements

    @app.callback(
        Output('download-csv', 'data'),
        Input('save-csv-button', 'n_clicks'),
        State('cytoscape-graph', 'elements'),
        State('json-file-dropdown', 'value'),
        prevent_initial_call=True
    )
    def download_csv(n_clicks, elements, file_name):
        if n_clicks is None:
            raise PreventUpdate

        import csv
        from dash import dcc
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['Type', 'ID', 'Label', 'Source', 'Target', 'Relation Type'])

        for element in elements:
            if 'data' in element:
                data = element['data']
                if 'source' in data:
                    writer.writerow([
                        'Edge',
                        data.get('id', ''),
                        data.get('label', ''),
                        data.get('source', ''),
                        data.get('target', ''),
                        data.get('relation_type', '')
                    ])
                else:
                    writer.writerow([
                        'Node',
                        data.get('id', ''),
                        data.get('label', ''),
                        '', '', ''
                    ])

        return dcc.send_string(output.getvalue(), filename="graph_export.csv")

    @app.callback(
        Output('cytoscape-graph', 'tapNodeData'),
        Input('cytoscape-graph', 'tapNode'),
        State('cytoscape-graph', 'tapNodeData')
    )
    def update_tap_node_data(tap_node, tap_node_data):
        if tap_node:
            return tap_node_data
        return None

    @app.callback(
        Output('cytoscape-graph', 'selectedNodeData'),
        Input('cytoscape-graph', 'selectedNodeData'),
        State('cytoscape-graph', 'selectedNodeData')
    )
    def update_selected_node_data(selected_node_data, current_selected_node_data):
        if selected_node_data:
            return selected_node_data
        return current_selected_node_data

    @app.callback(
        Output('json-file-dropdown', 'options'),
        Input('apply-button', 'n_clicks')
    )
    def update_json_files(n_clicks):
        return get_json_files()

    @app.callback(
        Output('apply-button', 'style'),
        Input('apply-button', 'n_clicks'),
        State('apply-button', 'style')
    )
    def update_button_style(n_clicks, current_style):
        if n_clicks and n_clicks > 0:
            return {
                **current_style,
                'backgroundColor': '#14444C',
                'transform': 'scale(0.98)'
            }
        return current_style