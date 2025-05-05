from dash import html, no_update, callback, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from flask_login import login_user, logout_user, current_user
from app import User
from layouts.admin_layout import get_participants_by_group

# Callback to update participant dropdown based on selected group
@callback(
    Output("participant-dropdown-container", "children"),
    Input("group-dropdown", "value"),
    Input("show-all-checkbox", "value")
)
def update_participant_dropdown(selected_group, show_all):
    import dash_bootstrap_components as dbc
    
    if 1 in show_all:
        return html.Div("Showing data for all participants")
    
    if not selected_group:
        return html.Div("No group selected")
    
    try:
        # Get participants in the selected group
        groups = get_participants_by_group(selected_group)
        
        if not groups or selected_group not in groups:
            return html.Div("No participants in the selected group")
        
        participants = groups[selected_group]['participants']
        
        if not participants:
            return html.Div("No participants in the selected group")
        
        # Create dropdown component
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
    except Exception as e:
        print(f"Error updating participant dropdown: {e}")
        return html.Div(f"Error loading participants: {str(e)}")

# Callback to store the selected participant ID
@callback(
    Output('selected-participant-store', 'data'),  # Change from 'children' to 'data'
    [Input('participant-dropdown', 'value'),
     Input('show-all-checkbox', 'value')],
    [State('group-dropdown', 'value')]
)
def update_participant_store(participant_id, show_all, group_id):
    if 1 in show_all or not group_id:
        return None
        
    if participant_id:
        return participant_id
    
    # If participant_id is None but we should have one, try to get the first participant
    if group_id:
        try:
            groups = get_participants_by_group(group_id)
            if group_id in groups and groups[group_id]['participants']:
                return groups[group_id]['participants'][0]['id']
        except Exception as e:
            print(f"Error getting first participant: {e}")
    
    return None

# Callback to update the selected view info
@callback(
    Output("selected-view-info", "children"),
    [Input("group-dropdown", "value"),
     Input("show-all-checkbox", "value"),
     Input("selected-participant-store", "data")]  # Changed from 'children' to 'data'
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
        # Get participant name by ID
        from utils.database import get_user_by_id
        user_data = get_user_by_id(participant)
        if user_data:
            user = User(user_data)
            participant_name = user.display_name
        else:
            participant_name = f"Participant {participant}"
    except Exception as e:
        print(f"Error getting participant name: {e}")
        participant_name = f"Participant {participant}"
    
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
    
    # Login logic handled in index.py
    raise PreventUpdate

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