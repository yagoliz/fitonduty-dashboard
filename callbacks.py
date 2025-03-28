from dash import html, no_update, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from flask_login import login_user, logout_user, current_user
from app import USERS
from layouts.admin_layout import get_participants_by_group

# Callback to update participant dropdown based on selected group
@callback(
    Output("participant-dropdown-container", "children"),
    Input("group-dropdown", "value"),
    Input("show-all-checkbox", "value")
)
def update_participant_dropdown(selected_group, show_all):
    from dash import dcc, html
    import dash_bootstrap_components as dbc
    
    if 1 in show_all:
        return html.Div("Showing data for all participants")
    
    if not selected_group:
        return html.Div("No group selected")
    
    groups = get_participants_by_group()
    participants = groups.get(selected_group, [])
    
    return html.Div([
        dbc.Label("Participant"),
        dcc.Dropdown(
            id="participant-dropdown",
            options=[
                {"label": participant["username"], "value": participant["id"]}
                for participant in participants
            ],
            value=participants[0]["id"] if participants else None,
            clearable=False
        )
    ])

# Callback to update the selected participant store
@callback(
    Output('selected-participant-store', 'children'),
    Input('participant-dropdown', 'value'),
    # Only run if the container exists
    State('participant-dropdown-container', 'children')
)
def update_participant_store(participant, container):
    if not container or participant is None:
        return ""
    return participant

# Callback to update the selected view info
@callback(
    Output("selected-view-info", "children"),
    Input("group-dropdown", "value"),
    Input("show-all-checkbox", "value"),
    Input("selected-participant-store", "children")
)
def update_selected_view_info(group, show_all, participant):
    from dash import html
    
    if 1 in show_all:
        return html.Div([
            html.H4("Viewing: All Participants"),
            html.P("Displaying aggregated data across all groups and participants.")
        ])
    
    if not group:
        return html.Div("Please select a group")
    
    if not participant:
        return html.Div([
            html.H4(f"Viewing: Group {group}"),
            html.P("Please select a participant or choose 'Show all participants'.")
        ])
    
    try:
        participant_name = USERS.get(participant).username if participant in USERS else participant
    except AttributeError:
        participant_name = "Unknown participant"
    
    return html.Div([
        html.H4(f"Viewing: {participant_name}"),
        html.P(f"Individual data for participant in Group {group}.")
    ])

# Display user info for admin
@callback(
    Output('user-info', 'children'),
    Input('url', 'pathname')
)
def update_user_info(pathname):
    from dash import html
    
    if current_user.is_authenticated:
        return html.P(f"Logged in as: {current_user.username}")
    return html.P("Not logged in")

# Display participant info 
@callback(
    Output('participant-info', 'children'),
    Input('url', 'pathname')
)
def update_participant_info(pathname):
    from dash import html
    
    if current_user.is_authenticated and current_user.role == 'participant':
        return [
            html.H5(f"Welcome, {current_user.username}!"),
            html.P(f"You are in Group {current_user.group}")
        ]
    return html.P("Not logged in")

# Login callback
# Then update the login callback:

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
    
    # Check if user exists and password is correct
    if username in USERS and USERS[username].check_password(password):
        user = USERS[username]
        login_user(user)
        return '/', f'Logged in as {username}'
    
    # Don't redirect on failed login - keep user on same page
    # Just update the error message
    return no_update, html.Div('Incorrect user or password', style={'color': 'red', 'fontWeight': 'bold', 'textAlign': 'center'})

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