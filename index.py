from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash
from flask_login import logout_user, current_user
from app import app, login_and_create_session
from utils.database import get_user_by_username

# Import layouts
from layouts import login_layout, admin_layout, participant_layout, error_layouts

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/login' or not current_user.is_authenticated:
        return login_layout.layout
    
    # User is authenticated, check role
    if current_user.is_authenticated:  # This is redundant but clarifies intent
        if current_user.role == 'admin':
            if pathname == '/':
                return admin_layout.create_layout()
            # Add other admin paths here
        else:  # Participant view
            if pathname == '/':
                return participant_layout.create_layout()
    
    # No matching route found
    return error_layouts.not_found_layout

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
    if not n_clicks or not username or not password:
        raise PreventUpdate
    
    try:
        # Retrieve user data from database
        user_data = get_user_by_username(username)
        
        if not user_data:
            print(f"User {username} not found in database.")
            return dash.no_update, html.Div(
                'Login failed', 
                style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}
            )
        
        # Create user object
        from app import User
        user = User(user_data)
        
        # Check password
        if user.check_password(password):
            # Log user in and create session
            success = login_and_create_session(user)
            
            if success:
                return '/', f'Logged in as {user.display_name}'
            else:
                print("Login session creation failed.")
                return dash.no_update, html.Div(
                    'Login failed', 
                    style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}
                )
        else:
            print(f"Password check failed for user {username}.")
            return dash.no_update, html.Div(
                'Login failed', 
                style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}
            )
            
    except Exception as e:
        print(f"Login error: {e}")
        return dash.no_update, html.Div(
            'An error occurred during login', 
            style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'}
        )

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