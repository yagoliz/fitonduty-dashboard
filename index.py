from dash import dcc, html, callback, Input, Output
import flask
from flask_login import current_user

from app import app, server
from layouts.login_layout import login_layout
from layouts.admin_layout import create_layout as create_admin_layout
from layouts.participant_layout import create_layout as create_participant_layout
from layouts.error_layouts import not_found_layout, forbidden_layout
import callbacks  # This imports and registers all callbacks

# Routes for Flask server
@server.route('/login')
def login_page():
    if current_user.is_authenticated:
        return flask.redirect('/')
    return flask.redirect('/')

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback for URL routing
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # Check if user is authenticated
    if not current_user.is_authenticated:
        return login_layout
    
    # Check if the user has admin role
    is_admin = getattr(current_user, 'role', None) == 'admin'
    
    # For authenticated users, route based on path and role
    if pathname == '/':
        if is_admin:
            return create_admin_layout()
        else:
            return create_participant_layout(current_user.id)
    elif pathname == '/admin':
        if is_admin:
            return create_admin_layout()
        else:
            return forbidden_layout
    
    # If no matching route, return not found
    return not_found_layout

# Run the app
if __name__ == '__main__':
    app.run(debug=True)