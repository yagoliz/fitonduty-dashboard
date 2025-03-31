# index.py
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user, current_user
from app import app, server, USERS

# Import layouts
from layouts import login_layout
from layouts.admin_layout import layout as admin_layout
from layouts import participant_layout
from layouts.footer import create_footer

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className="d-flex flex-column min-vh-100"),
    # Add footer
    create_footer()
])

# Callback for URL routing
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/login' or not current_user.is_authenticated:
        return login_layout.layout
    
    # User is authenticated, show appropriate view
    if current_user.role == 'admin':
        if pathname == '/':
            return admin_layout
    else:
        if pathname == '/':
            return participant_layout.create_layout(current_user.id)
            
    # Default to login if no match
    return login_layout.layout

# Login callback
@callback(
    Output('url', 'pathname'),
    Output('login-status', 'children'),
    Input('login-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    if not n_clicks or not username:
        raise PreventUpdate
    
    # Very simple auth - in production, verify against a secure database
    # and use proper password hashing
    if username in USERS:
        user = USERS[username]
        # In real app, check password hash
        login_user(user)
        return '/', f'Logged in as {username}'
    
    return '/login', 'Invalid credentials'

# Logout callback
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        logout_user()
        return '/login'
    raise PreventUpdate

if __name__ == '__main__':
    app.run(debug=True)