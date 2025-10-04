from styles.style import common_styles, h1_style, style_alert_base, description_style, button_style, button_style2, \
    text_content_style, button_style_backtohome

layout_style = {**common_styles, 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}
h1_centered_style = {**h1_style, 'textAlign': 'center'}
main_container_style = {'display': 'flex', 'flexDirection': 'row', 'marginTop': '20px', 'flex': '1'}
left_panel_style = {
    'flex': '0.7',
    'padding': '10px',
    'borderRight': '1px solid #ccc',
    'backgroundColor': '#f9f9f9'
}
right_panel_style = {
    'flex': '2.3',
    'padding': '10px',
    'backgroundColor': 'white'
}
dropdown_style = {'width': '100%', 'marginBottom': '20px', 'fontSize': '14px'}
upload_style = {
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
}
button_column_style = {'display': 'flex', 'flexDirection': 'column', 'marginTop': '10px'}
radio_label_style = {'display': 'block', 'marginBottom': '10px'}
radio_style = {'textAlign': 'left'}
text_container_style = {
    'border': '1px solid #ccc',
    'padding': '10px',
    'overflow': 'auto',
    'maxHeight': '500px',
    'backgroundColor': 'white'
}
file_info_style = {'fontSize': '14px', 'color': '#555'}
progress_container_style = {'display': 'none', 'marginTop': '20px'}
progress_label_style = {'fontWeight': 'bold'}
stop_button_hidden_style = {'display': 'none'}
stop_button_visible_style = {'display': 'block', **button_style2}