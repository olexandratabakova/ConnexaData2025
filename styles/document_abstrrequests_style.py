# Основні кольори
colors = {
    'primary': '#3182ce',
    'primary_hover': '#2c5aa0',
    'secondary': '#e2e8f0',
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#f56565',
    'dark_text': '#2d3748',
    'gray_text': '#718096',
    'gray_light': '#f7fafc',
    'gray_medium': '#edf2f7',
    'gray_border': '#e2e8f0',
    'white': '#ffffff'
}

# Основні стилі контейнерів
main_container_style = {
    'height': '100vh',  # Може бути забагато
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'backgroundColor': colors['white'],
    'fontFamily': 'Segoe UI, system-ui, sans-serif',
    'padding': '20px'
}

title_style = {
    'fontSize': '42px',
    'fontWeight': '700',
    'color': colors['dark_text'],
    'margin': '40px 0 20px 0',
    'textAlign': 'center'
}

content_wrapper_style = {
    'display': 'flex',
    'width': '100%',  # Може бути недостатньо
    'maxWidth': '1200px',
    'height': 'auto',  # Проблема - може розтягуватись
    'marginTop': '20px',
    'gap': '30px'
}

# Стилі лівої панелі
input_panel_style = {
    'flex': '1',
    'padding': '40px',
    'backgroundColor': colors['white'],
    'borderRadius': '12px',
    'border': f'1px solid {colors["gray_border"]}',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'display': 'flex',
    'flexDirection': 'column',
    'overflowY': 'auto',  # Додати прокрутку при потребі
    'maxHeight': '100%',  # Обмежити висоту
    'boxSizing': 'border-box',
    'width': 'auto'
}


# Загальні стилі елементів
label_style = {
    'fontWeight': '600',
    'color': colors['dark_text'],
    'margin': '0 0 8px 0',
    'display': 'block',
    'fontSize': '16px'
}

left_aligned_label_style = {
    **label_style,
    'textAlign': 'left',
    'alignSelf': 'flex-start',
    'width': '100%'
}

input_field_style = {
    'width': '100%',
    'height': '45px',
    'border': f'2px solid {colors["gray_border"]}',
    'borderRadius': '8px',
    'padding': '0 15px',
    'fontSize': '16px',
    'marginBottom': '20px',
    'backgroundColor': colors['white'],
    'color': colors['dark_text']
}

text_area_style = {
    'width': '100%',
    'height': '120px',
    'border': f'2px solid {colors["gray_border"]}',
    'borderRadius': '8px',
    'padding': '15px',
    'fontSize': '16px',
    'marginBottom': '20px',
    'resize': 'vertical',
    'backgroundColor': colors['white'],
    'color': colors['dark_text'],
    'fontFamily': 'inherit'
}

dropdown_style = {
    'width': '100%',
    'marginBottom': '15px',
    'fontSize': '14px'
}

upload_area_style = {
    'width': '100%',
    'height': '80px',
    'lineHeight': '80px',
    'border': f'2px dashed {colors["gray_border"]}',
    'borderRadius': '8px',
    'textAlign': 'center',
    'marginBottom': '20px',
    'backgroundColor': colors['gray_light'],
    'color': colors['gray_text'],
    'fontSize': '16px'
}

link_style = {
    'color': colors['primary'],
    'textDecoration': 'underline',
    'fontWeight': '500'
}

# Стилі кнопок
generate_button_style = {
    'border': 'none',
    'width': '150px',
    'padding': '12px 24px',
    'fontSize': '16px',
    'fontWeight': '600',
    'borderRadius': '8px',
    'cursor': 'pointer',
    'backgroundColor': colors['primary'],
    'color': colors['white'],
    'marginTop': 'auto',
    'transition': 'all 0.3s ease'
}

generate_button_style_hover = {
    **generate_button_style,
    'backgroundColor': colors['primary_hover'],
    'transform': 'translateY(-2px)'
}

# Стилі для нових елементів
decision_buttons_container_style = {
    'backgroundColor': colors['gray_light'],
    'padding': '15px',
    'borderRadius': '8px',
    'border': f'1px solid {colors["gray_border"]}',
    'width': '100%'
}

decision_buttons_style = {
    'display': 'flex',
    'gap': '12px',
    'marginTop': '20px',
    'justifyContent': 'center',
    'flexWrap': 'wrap'
}

decision_button_base_style = {
    'padding': '10px 20px',
    'border': 'none',
    'borderRadius': '6px',
    'cursor': 'pointer',
    'fontSize': '14px',
    'fontWeight': '600',
    'minWidth': '140px',
    'transition': 'all 0.3s ease'
}

yes_button_style = {
    **decision_button_base_style,
    'backgroundColor': '#c1e2e8',
    'color': 'black',
    'boxShadow': '0 0 3px 3px #d8d9f2',

}

expand_button_style = {
    **decision_button_base_style,
    'backgroundColor': '#c8dbfa',
    'color': 'black',
    'boxShadow': '0 0 3px 3px #d8d9f2',

}

no_button_style = {
    **decision_button_base_style,
    'backgroundColor': "#b8b9f5",
    'color': 'black',
    'boxShadow': '0 0 3px 3px #d8d9f2',

}

regenerate_button_style = {
    **decision_button_base_style,
    'backgroundColor': colors['primary'],
    'color': colors['white'],
    'width': '200px',
    'margin': '0 auto',
    'display': 'block'
}


file_info_style = {
    'fontSize': '14px',
    'color': colors['gray_text'],
    'marginTop': '10px',
    'textAlign': 'left'
}

# Стилі прогресс-барів
progress_bar_placeholder_style = {
    'height': '8px',
    'backgroundColor': colors['gray_medium'],
    'borderRadius': '4px',
    'margin': '20px 0',
    'border': f'1px solid {colors["gray_border"]}',
    'overflow': 'hidden'
}

# Стилі для нового контенту
new_content_container_style = {
    'padding': '20px',
    'backgroundColor': colors['white'],
    'borderRadius': '8px',
    'border': f'1px solid {colors["gray_border"]}',
    'minHeight': '150px',
    'marginBottom': '20px'
}

future_prompt_style = {
    'minHeight': '80px',
    'marginTop': '15px',
    'padding': '15px',
    'border': f'2px dashed {colors["gray_border"]}',
    'borderRadius': '8px',
    'backgroundColor': colors['gray_light'],
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center'
}

progress_styles = {
    'container': {
        'marginTop': '15px',
        'marginBottom': '15px'
    },
    'text': {
        'textAlign': 'center',
        'marginBottom': '5px',
        'fontWeight': 'bold',
        'color': '#007bff'
    },
    'placeholder': {
        'width': '100%',
        'height': '20px',
        'backgroundColor': '#e9ecef',
        'borderRadius': '10px',
        'overflow': 'hidden'
    },
    'bar_default': {
        'height': '100%',
        'borderRadius': '10px',
        'width': '0%',
        'transition': 'width 0.3s ease'
    },
    'bar_25': {
        'height': '100%',
        'backgroundColor': '#007bff',
        'borderRadius': '10px',
        'width': '25%',
        'transition': 'width 0.3s ease'
    },
    'bar_50': {
        'height': '100%',
        'backgroundColor': '#007bff',
        'borderRadius': '10px',
        'width': '50%',
        'transition': 'width 0.3s ease'
    },
    'bar_75': {
        'height': '100%',
        'backgroundColor': '#007bff',
        'borderRadius': '10px',
        'width': '75%',
        'transition': 'width 0.3s ease'
    },
    'bar_100': {
        'height': '100%',
        'backgroundColor': '#28a745',
        'borderRadius': '10px',
        'width': '100%',
        'transition': 'width 0.3s ease'
    }
}

# Додайте ці стилі до вашого словника стилів:

# Стилі для контейнера інформації про файл
file_info_container_style = {
    'fontSize': '14px',
    'color': colors['gray_text'],
    'backgroundColor': colors['gray_light'],
    'padding': '8px 12px',
    'borderRadius': '6px',
    'border': f'1px solid {colors["gray_border"]}',
    'textAlign': 'center',
    'width': 'auto',
    'flexShrink': 0
}

# Оновлені стилі для контенту документа
document_content_style = {
    'lineHeight': '1.6',
    'color': colors['dark_text'],
    'fontSize': '16px',
    'whiteSpace': 'pre-wrap',
    'textAlign': 'left',
    'height': 'calc(100vh - 250px)',  # Адаптивна висота
    'minHeight': '400px',
    'overflowY': 'auto',
    'padding': '15px',
    'backgroundColor': colors['white'],
    'border': f'1px solid {colors["gray_border"]}',
    'borderRadius': '8px',
    'flex': '1'
}

# Оновлені стилі для правої панелі
output_panel_style = {
    'flex': '1',
    'padding': '25px',
    'backgroundColor': colors['white'],
    'borderRadius': '12px',
    'border': f'1px solid {colors["gray_border"]}',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'display': 'flex',
    'flexDirection': 'column',
    'boxSizing': 'border-box',
    'minHeight': '600px'
}

# Оновлені стилі заголовка документа
document_title_style = {
    'marginBottom': '0',
    'color': colors['dark_text'],
    'fontSize': '20px',
    'fontWeight': '600',
    'textAlign': 'left',
    'flex': '1'
}