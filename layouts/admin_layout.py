# layouts/admin_layout.py
from dash import dcc, html, callback, Input, Output, State, ALL, MATCH, no_update
import dash_bootstrap_components as dbc
from flask_login import current_user
from app import USERS
import dash
from dash.exceptions import PreventUpdate

# Import components
from layouts.components.day_selector import create_day_selector
from layouts.components.participant_metrics import create_participant_metrics_layout
from layouts.components.group_metrics import create_group_metrics_layout
from layouts.components.participant_ranking import create_participant_ranking_layout

# Get all participants grouped by their group
def get_participants_by_group():
    from app import USERS
    groups = {}
    for user_id, user in USERS.items():
        if user.role == 'participant':
            if user.group not in groups:
                groups[user.group] = []
            groups[user.group].append({'id': user.id, 'username': user.username})
    return groups

# Sidebar layout - Create with initial dropdown
def create_sidebar():
    groups = get_participants_by_group()
    first_group = list(groups.keys())[0] if groups else None
    
    # If there's a group, get its participants
    participants = []
    if first_group:
        participants = groups.get(first_group, [])
    
    sidebar_content = [
        html.H4("Admin Dashboard", className="text-center"),
        html.Hr(),
        # Placeholder for user info that will be filled by callback
        html.Div(id="user-info-display", className="text-center"),
        html.Hr(),
        
        # Groups and participants selection
        html.H5("Select Data View"),
        dbc.Label("Group"),
        # Include the group dropdown directly
        dcc.Dropdown(
            id="group-dropdown",
            options=[
                {"label": f"Group {group}", "value": group}
                for group in groups.keys()
            ],
            value=first_group,
            clearable=False
        ),
        
        # Create a placeholder for participant dropdown
        html.Div(id="participant-dropdown-container", className="mt-3"),
        
        # Create a hidden div to store selected participant
        html.Div(id="selected-participant-store", style={"display": "none"}),
        
        # Show all participants option
        dbc.Checklist(
            options=[{"label": "Show all participants", "value": 1}],
            value=[],
            id="show-all-checkbox",
            switch=True,
            className="mt-3"
        ),
        
        html.Hr(),
        
        # Logout button
        dbc.Button(
            "Logout", 
            id="logout-button", 
            color="danger", 
            className="w-100 mt-3"
        )
    ]
    
    return dbc.Col(
        dbc.Card(dbc.CardBody(sidebar_content)),
        width=12, xl=3,
        className="bg-light mb-4"
    )

# Main content layout
def create_main_content():
    return dbc.Col(
        [
            html.H2("Sensor Data Dashboard", className="text-center mb-4"),
            
            # Date selector
            html.Div(
                create_day_selector(id_prefix="participant"),
                id="date-selector-container"
            ),
            
            # Display selected view information
            html.Div(id="selected-view-info", className="mb-4"),
            
            # Metrics dashboard - will be filled by callback
            html.Div(id="metrics-container"),

            # Participant Ranking Section (always visible)
            html.Div(
                create_participant_ranking_layout(),
                id="ranking-container",
                className="mb-4"
            )
        ],
        width=12, xl=9
    )

# Complete admin layout
layout = dbc.Container(
    [
        dbc.Row(
            [
                create_sidebar(),
                create_main_content()
            ],
            className="g-4"
        )
    ],
    fluid=True,
    className="py-3"
)

# Callback to display user info
@callback(
    Output("user-info-display", "children"),
    Input("url", "pathname")
)
def update_user_info(pathname):
    if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        return html.P(f"Logged in as: {current_user.username}")
    return html.P("Not logged in")

# Callback to update participant dropdown based on selected group
@callback(
    [Output("participant-dropdown-container", "children"),
     Output("selected-participant-store", "children")],
    [Input("group-dropdown", "value"),
     Input("show-all-checkbox", "value")],
    [State("selected-participant-store", "children")]
)
def update_participant_dropdown(selected_group, show_all, current_participant):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if 1 in show_all:
        return html.Div("Showing data for all participants"), None
    
    if not selected_group:
        return html.Div("No group selected"), None
    
    groups = get_participants_by_group()
    participants = groups.get(selected_group, [])
    
    # Determine the value for the dropdown
    default_value = participants[0]["id"] if participants else None
    
    # Keep selected participant if group didn't change
    if triggered != "group-dropdown" and current_participant:
        # Check if current participant is in this group
        participant_ids = [p["id"] for p in participants]
        if current_participant in participant_ids:
            default_value = current_participant
    
    # Create participant dropdown
    dropdown = html.Div([
        dbc.Label("Participant"),
        dcc.Dropdown(
            id="participant-dropdown",
            options=[
                {"label": participant["username"], "value": participant["id"]}
                for participant in participants
            ],
            value=default_value,
            clearable=False
        )
    ])
    
    return dropdown, default_value

# Store selected participant when dropdown changes
@callback(
    Output("selected-participant-store", "children", allow_duplicate=True),
    Input("participant-dropdown", "value"),
    prevent_initial_call=True
)
def store_selected_participant(participant_id):
    if not participant_id:
        raise PreventUpdate
    return participant_id

# Callback to update the selected view info
@callback(
    Output("selected-view-info", "children"),
    [Input("group-dropdown", "value"),
     Input("selected-participant-store", "children"),
     Input("show-all-checkbox", "value"),
     Input("participant-date-picker", "date")]
)
def update_selected_view_info(group, participant, show_all, date):
    date_str = f" - Data for {date}" if date else ""
    
    if 1 in show_all:
        return html.Div([
            html.H4(f"Viewing: All Participants{date_str}"),
            html.P("Displaying aggregated data across all groups and participants.")
        ], className="alert alert-info")
    
    if not group:
        return html.Div("Please select a group", className="alert alert-warning")
    
    if not participant:
        return html.Div([
            html.H4(f"Viewing: Group {group}{date_str}"),
            html.P("Please select a participant or choose 'Show all participants'.")
        ], className="alert alert-warning")
    
    # Safe way to get participant name
    participant_name = "Unknown"
    if participant in USERS:
        participant_name = USERS[participant].username
    
    return html.Div([
        html.H4(f"Viewing: {participant_name} (Group {group}){date_str}"),
        html.P("Individual health data for selected participant.")
    ], className="alert alert-success")

# Callback to toggle between participant and group metrics
@callback(
    Output("metrics-container", "children"),
    [Input("show-all-checkbox", "value"),
     Input("group-dropdown", "value"),
     Input("selected-participant-store", "children")]
)
def update_metrics_view(show_all, group, participant):
    """
    Toggle between individual participant metrics and group metrics based on selection
    """
    # Show group metrics if "Show all participants" is checked or no participant is selected
    if 1 in show_all:
        return create_group_metrics_layout()
    
    # Show group metrics if a group is selected but no specific participant
    if group and not participant:
        return create_group_metrics_layout()
    
    # Otherwise show individual participant metrics
    return create_participant_metrics_layout()

# Callback to toggle the visibility of ranking section based on view
@callback(
    Output("ranking-container", "style"),
    [Input("show-all-checkbox", "value"),
     Input("group-dropdown", "value")]
)
def toggle_ranking_visibility(show_all, group):
    """
    Show ranking only when viewing a group (not an individual participant)
    or when "Show all participants" is checked
    """
    # Always show for group view or "show all" mode
    if 1 in show_all or (group and not 1 in show_all):
        return {"display": "block"}
    
    # Hide when no group is selected
    if not group:
        return {"display": "none"}
    
    # Default to showing
    return {"display": "block"}