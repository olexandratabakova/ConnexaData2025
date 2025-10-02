from dash import dcc, Input, Output, State, html
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

from components.dropdown import create_dropdown
from components.node_panels import create_rename_panel
from utils.viz.nodes import *
from components.nav import NAV_COMPONENT

def create_layout(file_name, min_color, max_color, max_objects, avg_size, node_spacing):
    nodes, edges, error_message = load_data(file_name, min_color, max_color, max_objects, avg_size)
    if error_message:
        return error_message

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
                id='node-info-container',
                style={
                    'position': 'fixed',
                    'top': '20px',
                    'background': 'white',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
                    'maxWidth': '300px',
                    'zIndex': 1000,
                    'display': 'none',
                    'fontFamily': 'Helvetica',
                    'fontSize': '13px',
                }
            ),
        ]
    )

layout = html.Div(
    style={
        'display': 'flex',
        'flexDirection': 'row',
        'height': '100vh',
        'fontFamily': 'Helvetica',
        'backgroundColor': '#FFFAEB',
    },
    children=[
        NAV_COMPONENT,
        dcc.Download(id="download-csv"),
        html.Div(
            id='sidebar',
            style=sidebar_style,
            children=[
                html.H3("Visualization", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginBottom': '20px',
                                                'textAlign': 'center'}),
                create_dropdown(),
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
                    style={'width': '100%', 'marginBottom': '20px', 'fontFamily': 'Helvetica'},
                    clearable=False,
                ),

                html.H3("Size Settings", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginBottom': '20px',
                                                'textAlign': 'center', 'marginTop': '-10px'}),

                html.Label("Text Size", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left'}),
                html.Div(
                    dcc.Slider(
                        id='text-size-slider',
                        min=10,
                        max=30,
                        step=1,
                        value=12,
                        marks={i: str(i) for i in range(10, 31, 5)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Node Size", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left',
                                               'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='node-size-slider',
                        min=10,
                        max=150,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 151, 20)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Edge Thickness", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left',
                                                    'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='edge-thickness-slider',
                        min=1,
                        max=10,
                        step=1,
                        value=2,
                        marks={i: str(i) for i in range(1, 11, 1)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Node Spacing", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left', 'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='node-spacing-slider',
                        min=100,
                        max=5000,
                        step=50,
                        value=100,
                        marks={i: str(i) for i in range(100, 5000, 500)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.Label("Average Node Size",
                           style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left',
                                  'marginTop': '10px'}),
                html.Div(
                    dcc.Slider(
                        id='avg-size-slider',
                        min=10,
                        max=100,
                        step=5,
                        value=30,
                        marks={i: str(i) for i in range(10, 101, 10)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),

                html.H3("Colors", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'marginBottom': '20px',
                                         'textAlign': 'center'}),

                html.Div(
                    style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                           'marginTop': '10px', 'width': '100%'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
                                   'width': '48%'},
                            children=[
                                html.Label("Min Color", style={'color': '#1B5E67', 'fontFamily': 'Helvetica',
                                                               'marginBottom': '10px'}),
                                daq.ColorPicker(
                                    id='min-color-picker',
                                    value=dict(hex='#FF69B4'),
                                    style={'border': 'none', 'boxShadow': 'none', 'width': '100%'}
                                )
                            ]
                        ),
                        html.Div(
                            style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
                                   'width': '48%'},
                            children=[
                                html.Label("Max Color", style={'color': '#1B5E67', 'fontFamily': 'Helvetica',
                                                               'marginBottom': '10px'}),
                                daq.ColorPicker(
                                    id='max-color-picker',
                                    value=dict(hex='#1E90FF'),
                                    style={'border': 'none', 'boxShadow': 'none', 'width': '100%'}
                                )
                            ]
                        )
                    ]
                ),

                html.Label("Max Objects", style={'color': '#1B5E67', 'fontFamily': 'Helvetica', 'textAlign': 'left'}),
                html.Div(
                    dcc.Slider(
                        id='max-objects-slider',
                        min=10,
                        max=500,
                        step=10,
                        value=50,
                        marks={i: str(i) for i in range(10, 501, 50)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                    ),
                    style={'width': '90%', 'marginBottom': '20px'}
                ),
                html.Button("Apply", id='apply-button', style={**button_style_backtohome, "border": "none"}),
            ]
        ),

        html.Div(
            id='main-content',
            style=main_content_style,
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
        State('file-dropdown', 'value'),
        State('min-color-picker', 'value'),
        State('max-color-picker', 'value'),
        State('max-objects-slider', 'value'),
        State('avg-size-slider', 'value'),
        State('node-spacing-slider', 'value')
    )
    def update_visualization(n_clicks, selected_file, min_color, max_color, max_objects, avg_size, node_spacing):
        if n_clicks is None or not selected_file:
            return html.Div([
                html.Div("Please select a file and click 'Apply' to visualize.", style=error_message_style),
            ], style={'display': 'flex', 'flexDirection': 'column', 'justify-content': 'center',
                      'align-items': 'center', 'height': '100vh'})
        return create_layout(selected_file, min_color['hex'], max_color['hex'], max_objects, avg_size, node_spacing)

    @app.callback(
        Output('cytoscape-graph', 'stylesheet'),
        Input('apply-button', 'n_clicks'),
        State('text-size-slider', 'value'),
        State('node-size-slider', 'value'),
        State('edge-thickness-slider', 'value')
    )
    def update_stylesheet(n_clicks, text_size, node_size, edge_thickness):
        if n_clicks is None:
            return []

        return [
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

    @app.callback(
        Output('cytoscape-graph', 'layout'),
        Input('layout-dropdown', 'value')
    )
    def update_layout(selected_layout):
        return {'name': selected_layout}

    @app.callback(
        Output('node-info-container', 'children'),
        Output('node-info-container', 'style'),
        Input('cytoscape-graph', 'tapNodeData'),
    )
    def show_node_info(node_data):
        if not node_data:
            return [], {'display': 'none'}

        merged_parts = node_data.get('merged_parts', [])
        if not merged_parts:
            return [], {'display': 'none'}

        current_label = node_data.get('label', merged_parts[0])
        content = create_rename_panel(merged_parts, current_label)

        panel_style = {
            'display': 'block',
            'position': 'fixed',
            'right': '20px',
            'top': '20px',
            'background': 'white',
            'padding': '15px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'maxWidth': '300px',
            'zIndex': 1000,
        }

        return content, panel_style

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
        State('file-dropdown', 'value'),
        prevent_initial_call=True
    )

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