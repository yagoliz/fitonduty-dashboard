from dash import dcc, html
import dash_bootstrap_components as dbc
from app import USERS

# Get all participants grouped by their group
def get_participants_by_group():
    groups = {}
    for user_id, user in USERS.items():
        if user.role == 'participant':
            if user.group not in groups:
                groups[user.group] = []
            groups[user.group].append({'id': user.id, 'username': user.username})
    return groups

def create_layout():
    groups = get_participants_by_group()
    first_group = list(groups.keys())[0] if groups else None
    
    # Create sidebar content
    sidebar_content = [
        html.H4("Admin Dashboard", className="text-center"),
        html.Hr(),
        html.Div(id="user-info", className="text-center"),
        html.Hr(),
        
        # Groups and participants selection
        html.H5("Select Data View"),
        dbc.Label("Group"),
        dcc.Dropdown(
            id="group-dropdown",
            options=[
                {"label": f"Group {group}", "value": group}
                for group in groups.keys()
            ],
            value=first_group,
            clearable=False
        ),
        
        html.Div(id="participant-dropdown-container", className="mt-3"),
        
        # Show all participants option
        dbc.Checklist(
            options=[{"label": "Show all participants", "value": 1}],
            value=[],
            id="show-all-checkbox",
            switch=True,
            className="mt-3"
        ),
        
        # Hidden div to store selected participant
        html.Div(id='selected-participant-store', style={'display': 'none'}),
        
        html.Hr(),
        
        # Logout button
        dbc.Button(
            "Logout", 
            id="logout-button", 
            color="danger", 
            className="w-100 mt-3"
        )
    ]
    
    sidebar = dbc.Col(
        dbc.Card(dbc.CardBody(sidebar_content)),
        width=3,
        className="bg-light"
    )
    
    # Main content layout
    main_content = dbc.Col(
        [
            html.H2("Sensor Data Dashboard", className="text-center mb-4"),
            
            # Display selected view information
            html.Div(id="selected-view-info", className="mb-4"),
            
            # Placeholder for future charts and visualizations
            dbc.Card(
                dbc.CardBody([
                    html.H4("Data Visualizations", className="text-center"),
                    html.P("Charts will be displayed here based on selection.")
                ]),
                className="mb-4"
            )
        ],
        width=9
    )
    
    # Complete admin layout
    return dbc.Container(
        [
            dbc.Row(
                [
                    sidebar,
                    main_content
                ],
                className="h-100"
            )
        ],
        fluid=True,
        className="py-3"
    )