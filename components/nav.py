from dash import html

NAV_LINK_STYLE = {
    'padding': '8px',
    'fontSize': '16px',
    'color': '#1B5E67',
    'textDecoration': 'none',
    'fontFamily': 'Helvetica, Arial, sans-serif',
    'fontWeight': 'bold',
    'backgroundColor': '#E2F9FB',
    'borderRadius': '8px',
    'margin': '0 10px',
    'display': 'inline-block',
    'transition': 'all 0.3s ease',
}

NAV_STYLE = {
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'right': '0',
    'display': 'flex',
    'justifyContent': 'center',
    'gap': '15px',
    'padding': '10px 0',
    'backgroundColor': '#E2F9FB',
    'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
    'zIndex': '1000',
    'transition': 'transform 0.3s ease',
}

NAV_COMPONENT = html.Nav(
    id='main-nav',
    style=NAV_STYLE,
    children=[
        html.A("Home", href="/", style=NAV_LINK_STYLE, className='nav-link'),
        html.A("My document", href="/document", style=NAV_LINK_STYLE, className='nav-link'),
        html.A("Table", href="/table", style=NAV_LINK_STYLE, className='nav-link'),
        html.A("Statistics", href="/statistics", style=NAV_LINK_STYLE, className='nav-link'),
        html.A("Visualisation", href="/visualization", style=NAV_LINK_STYLE, className='nav-link'),
        html.A("Help", href="/help", style=NAV_LINK_STYLE, className='nav-link'),
    ]
)