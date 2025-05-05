# layouts/admin_layout.py
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate

from utils.database import get_participants_by_group, get_all_groups, load_participant_data
from layouts.footer import create_footer

DEFAULT_DATE = datetime(2025, 4, 1)

def create_layout():
    """
    Create the admin dashboard layout
    
    Returns:
        A dash component with the admin dashboard
    """
    # Create date picker with default to today
    today = datetime(2025, 4, 1).date()
    
    # Sidebar content
    sidebar_content = [
        html.H4("Admin Dashboard", className="text-center"),
        html.Hr(),
        html.Div(id="admin-user-info", className="text-center"),
        html.Hr(),
        
        # Date selection
        html.H5("Select Date"),
        dcc.DatePickerSingle(
            id="admin-date-picker",
            date=today,
            display_format="YYYY-MM-DD",
            className="mb-3 w-100"
        ),
        
        # Groups and participants selection
        html.H5("Select Data View"),
        dbc.Label("Group"),
        dcc.Dropdown(
            id="group-dropdown",
            options=[],  # Will be populated in callback
            clearable=False,
            className="mb-2"
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
        
        html.Hr(),
        
        # Data management section
        html.H5("Data Management"),
        dbc.Button(
            "Generate Mock Data", 
            id="generate-mock-data-btn", 
            color="secondary", 
            size="sm",
            className="w-100 mb-2"
        ),
        
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody([
                    dbc.Label("Date Range for Mock Data"),
                    dbc.Row([
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id="mock-data-start-date",
                                date=today - timedelta(days=30),
                                display_format="YYYY-MM-DD",
                                className="mb-2 w-100"
                            ),
                        ], width=6),
                        dbc.Col([
                            dcc.DatePickerSingle(
                                id="mock-data-end-date",
                                date=today,
                                display_format="YYYY-MM-DD",
                                className="mb-2 w-100"
                            ),
                        ], width=6),
                    ]),
                    dbc.Checklist(
                        options=[{"label": "Overwrite existing data", "value": 1}],
                        value=[],
                        id="overwrite-data-checkbox",
                        switch=True,
                        className="mt-2 mb-2"
                    ),
                    dbc.Button(
                        "Generate", 
                        id="confirm-generate-data-btn", 
                        color="primary", 
                        size="sm",
                        className="w-100"
                    ),
                    html.Div(id="generate-data-status", className="mt-2 small")
                ])
            ),
            id="mock-data-collapse",
            is_open=False,
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
    
    # Create sidebar
    sidebar = dbc.Col(
        dbc.Card(dbc.CardBody(sidebar_content)),
        width=3,
    )
    
    # Main content
    main_content = dbc.Col(
        [
            html.H2("Sensor Data Dashboard", className="text-center mb-4"),
            
            # Display selected view information
            html.Div(id="selected-view-info", className="mb-4"),
            
            # Data visualization sections
            html.Div(id="admin-data-visualizations"),
            
            # Add a Store component to hold the selected participant ID
            dcc.Store(id="selected-participant-store")
        ],
        width=9
    )
    
    # Complete admin layout
    return dbc.Container(
        [
            # Navigation bar
            dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            dbc.Col(html.Img(src="/assets/logo.svg", height="30px"), width="auto"),
                            dbc.Col(dbc.NavbarBrand("Health Dashboard Admin", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Collapse(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("User Management", href="/users", active="exact")),
                            dbc.NavItem(dbc.NavLink("Settings", href="/settings", active="exact")),
                        ],
                        className="me-auto",
                        navbar=True),
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ]),
                className="mb-4 bg-body-primary",
            ),
            
            # Main content with sidebar
            dbc.Row(
                [
                    sidebar,
                    main_content
                ],
                className="h-100"
            ),
            
            # Footer
            create_footer()
        ],
        fluid=True,
        className="vh-100 py-3"
    )

# Callback to update admin user info
@callback(
    Output("admin-user-info", "children"),
    Input("url", "pathname")
)
def update_admin_user_info(pathname):
    """Update admin user info display"""
    if current_user.is_authenticated and current_user.is_admin:
        return [
            html.H5(current_user.display_name, className="mb-0"),
            html.P("Administrator", className="text-muted")
        ]
    return html.P("Not logged in")

# Callback to populate the group dropdown
@callback(
    Output("group-dropdown", "options"),
    Output("group-dropdown", "value"),
    Input("url", "pathname")
)
def populate_group_dropdown(pathname):
    """Populate the group dropdown with all available groups"""
    try:
        # Get all groups from database
        groups = get_all_groups()
        
        # Create dropdown options
        options = [{"label": group["name"], "value": group["id"]} for group in groups]
        
        # Default to first group if available
        default_value = groups[0]["id"] if groups else None
        
        return options, default_value
    except Exception as e:
        print(f"Error populating group dropdown: {e}")
        return [], None

# Callback to update participant dropdown based on selected group
@callback(
    Output("participant-dropdown-container", "children"),
    Input("group-dropdown", "value"),
    Input("show-all-checkbox", "value")
)
def update_participant_dropdown(selected_group, show_all):
    """Update the participant dropdown based on selected group"""
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
                value=participants[0]["id"],
                clearable=False
            )
        ])
    except Exception as e:
        print(f"Error updating participant dropdown: {e}")
        return html.Div(f"Error loading participants: {str(e)}")

# Callback to update the selected view info
@callback(
    Output("selected-view-info", "children"),
    Input("group-dropdown", "value"),
    Input("selected-participant-store", "data"),
    Input("show-all-checkbox", "value"),
    Input("admin-date-picker", "date")
)
def update_selected_view_info(group_id, participant_id, show_all, date):
    """Update the information about what data is being displayed"""
    selected_date = date or datetime.now().date()
    date_str = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%B %d, %Y') if isinstance(selected_date, str) else selected_date.strftime('%B %d, %Y')
    
    if 1 in show_all:
        return html.Div([
            html.H4(f"Viewing: All Participants on {date_str}"),
            html.P("Displaying aggregated data across all groups and participants.")
        ])
    
    if not group_id:
        return html.Div("Please select a group")
    
    try:
        # Get group name
        groups = get_all_groups()
        group_name = next((g["name"] for g in groups if g["id"] == group_id), f"Group {group_id}")
        
        if not participant_id:
            return html.Div([
                html.H4(f"Viewing: {group_name} on {date_str}"),
                html.P("Please select a participant or choose 'Show all participants'.")
            ])
        
        # Get participant name
        participant_groups = get_participants_by_group(group_id)
        if group_id in participant_groups:
            participants = participant_groups[group_id]['participants']
            participant_name = next((p["username"] for p in participants if p["id"] == participant_id), f"Participant {participant_id}")
        else:
            participant_name = f"Participant {participant_id}"
        
        return html.Div([
            html.H4(f"Viewing: {participant_name} on {date_str}"),
            html.P(f"Individual data for participant in {group_name}.")
        ])
    except Exception as e:
        print(f"Error updating view info: {e}")
        return html.Div(f"Error: {str(e)}")

# Callback to update data visualizations
@callback(
    Output("admin-data-visualizations", "children"),
    [Input("group-dropdown", "value"),
     Input("show-all-checkbox", "value"),
     Input("admin-date-picker", "date"),
     Input("selected-participant-store", "data")]  # Changed from "selected-participant-store", "children"
)
def update_data_visualizations(group_id, show_all, date, participant_id):
    """Update the data visualizations based on selection"""
    if not date:
        date = datetime.now().date()
    
    # If showing all participants
    if 1 in show_all:
        # Return group comparison visualizations
        return create_group_comparison_visualizations(date)
    
    # If only group is selected
    if group_id and not participant_id:
        # Return group summary visualizations
        return create_group_summary_visualizations(group_id, date)
    
    # If participant is selected
    if participant_id:
        # Return participant detail visualizations
        return create_participant_detail_visualizations(participant_id, date)
    
    # Default - no selection
    return html.Div([
        dbc.Alert("Please select a group and/or participant to view data.", color="info")
    ])


def create_group_comparison_visualizations(date):
    """Create visualizations comparing all groups"""
    try:
        # Get all groups
        groups = get_all_groups()
        
        if not groups:
            return html.Div("No groups found")
        
        # Placeholder for group comparison data
        group_data = []
        
        # Load data for each group
        for group in groups:
            group_id = group["id"]
            
            # Get participants in this group
            participant_groups = get_participants_by_group(group_id)
            if group_id not in participant_groups:
                continue
                
            participants = participant_groups[group_id]['participants']
            
            # Accumulate data from all participants
            participant_data = []
            for participant in participants:
                # Load data for this participant
                df = load_participant_data(participant["id"], date, date)
                if not df.empty:
                    df['participant_id'] = participant["id"]
                    df['group_id'] = group_id
                    df['group_name'] = group["name"]
                    participant_data.append(df)
            
            # Combine all participant data for this group
            if participant_data:
                group_df = pd.concat(participant_data)
                
                # Calculate group averages
                avg_data = {
                    'group_id': group_id,
                    'group_name': group["name"],
                    'avg_resting_hr': group_df['resting_hr'].mean(),
                    'avg_max_hr': group_df['max_hr'].mean(),
                    'avg_sleep_hours': group_df['sleep_hours'].mean(),
                    'avg_hrv_rest': group_df['hrv_rest'].mean(),
                    'participant_count': len(participants)
                }
                group_data.append(avg_data)
        
        # Convert to DataFrame
        group_df = pd.DataFrame(group_data)
        
        if group_df.empty:
            return html.Div("No data available for the selected date")
        
        # Create visualizations
        return html.Div([
            # Group comparison cards
            dbc.Row([
                # Resting heart rate comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Average Resting Heart Rate by Group", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_resting_hr', 
                                    'Average Resting Heart Rate by Group',
                                    'bpm',
                                    '#1976D2'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
                # Sleep comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Average Sleep Hours by Group", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_sleep_hours', 
                                    'Average Sleep Hours by Group',
                                    'hours',
                                    '#4CAF50'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
            ]),
            
            # HRV and activity row
            dbc.Row([
                # HRV comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Average HRV by Group", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_hrv_rest', 
                                    'Average Heart Rate Variability by Group',
                                    'ms',
                                    '#673AB7'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
            ]),
            
            # Group metrics table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Group Summary Metrics", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dbc.Table.from_dataframe(
                                    group_df[[
                                        'group_name', 'participant_count', 'avg_resting_hr', 
                                        'avg_sleep_hours', 'avg_hrv_rest'
                                    ]].round(1),
                                    striped=True,
                                    bordered=True,
                                    hover=True,
                                    responsive=True,
                                    header={
                                        'group_name': 'Group',
                                        'participant_count': 'Participants',
                                        'avg_resting_hr': 'Avg Resting HR (bpm)',
                                        'avg_sleep_hours': 'Avg Sleep (hrs)',
                                        'avg_hrv_rest': 'Avg HRV (ms)',
                                    }
                                )
                            ])
                        ])
                    ])
                ], width=12, className="mb-4"),
            ]),
        ])
    except Exception as e:
        print(f"Error creating group comparison visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading group data: {str(e)}", color="danger")
        ])

def create_group_summary_visualizations(group_id, date):
    """Create visualizations summarizing a single group"""
    try:
        # Get participants in the group
        participant_groups = get_participants_by_group(group_id)
        
        if group_id not in participant_groups:
            return html.Div("No participants found in this group")
            
        group_name = participant_groups[group_id]['name']
        participants = participant_groups[group_id]['participants']
        
        if not participants:
            return html.Div("No participants found in this group")
        
        # Accumulate data from all participants
        participant_data = []
        for participant in participants:
            # Load data for this participant
            df = load_participant_data(participant["id"], date, date)
            if not df.empty:
                df['participant_id'] = participant["id"]
                df['participant_name'] = participant["username"]
                participant_data.append(df)
        
        # Combine all participant data
        if not participant_data:
            return html.Div("No data available for the selected date")
            
        group_df = pd.concat(participant_data)
        
        # Create visualizations
        return html.Div([
            # Heart rate and sleep cards
            dbc.Row([
                # Heart rate comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate Comparison", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['resting_hr', 'max_hr'],
                                    ['Resting HR', 'Max HR'],
                                    ['#1976D2', '#D32F2F'],
                                    'Heart Rate Comparison',
                                    'bpm'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
                # Sleep comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Sleep Comparison", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['sleep_hours'],
                                    ['Sleep Hours'],
                                    ['#4CAF50'],
                                    'Sleep Hours Comparison',
                                    'hours'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
            ]),
            
            # HRV and activity row
            dbc.Row([
                # HRV comparison
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("HRV Comparison", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['hrv_rest'],
                                    ['HRV'],
                                    ['#673AB7'],
                                    'Heart Rate Variability Comparison',
                                    'ms'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
            ]),
            
            # Participant metrics table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5(f"Participant Metrics for {group_name}", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dbc.Table.from_dataframe(
                                    group_df[['participant_name', 'resting_hr', 'max_hr', 'sleep_hours', 'hrv_rest',]].groupby('participant_name').mean().reset_index().round(1),
                                    striped=True,
                                    bordered=True,
                                    hover=True,
                                    responsive=True,
                                    header={
                                        'participant_name': 'Participant',
                                        'resting_hr': 'Resting HR (bpm)',
                                        'max_hr': 'Max HR (bpm)',
                                        'sleep_hours': 'Sleep (hrs)',
                                        'hrv_rest': 'HRV (ms)',
                                    }
                                )
                            ])
                        ])
                    ])
                ], width=12, className="mb-4"),
            ]),
        ])
    except Exception as e:
        print(f"Error creating group summary visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading group data: {str(e)}", color="danger")
        ])

def create_participant_detail_visualizations(participant_id, date):
    """Create visualizations for a single participant"""
    try:
        # Get date range for historical data (last 30 days)
        end_date = date if isinstance(date, datetime) else datetime.strptime(date, '%Y-%m-%d').date()
        start_date = end_date - timedelta(days=30)
        
        # Load participant data
        df_single_day = load_participant_data(participant_id, end_date, end_date)
        df_history = load_participant_data(participant_id, start_date, end_date)
        
        if df_single_day.empty:
            return html.Div("No data available for the selected date")
        
        # Create visualizations
        return html.Div([
            # Summary cards
            dbc.Row([
                # Heart rate card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{df_single_day['resting_hr'].iloc[0]:.0f}", className="card-title text-center text-primary"),
                            html.P("Resting Heart Rate (bpm)", className="card-text text-center"),
                        ])
                    ], color="light", outline=True)
                ], width=6, md=3, className="mb-4"),
                
                # Sleep card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{df_single_day['sleep_hours'].iloc[0]:.1f}", className="card-title text-center text-success"),
                            html.P("Sleep Hours", className="card-text text-center"),
                        ])
                    ], color="light", outline=True)
                ], width=6, md=3, className="mb-4"),
                
                # HRV card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{df_single_day['hrv_rest'].iloc[0]:.0f}", className="card-title text-center text-info"),
                            html.P("HRV (ms)", className="card-text text-center"),
                        ])
                    ], color="light", outline=True)
                ], width=6, md=3, className="mb-4"),
                
            ]),
            
            # Historical charts
            dbc.Row([
                # Heart rate history
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate History", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_history_line_chart(
                                    df_history,
                                    ['resting_hr', 'max_hr'],
                                    ['Resting HR', 'Max HR'],
                                    ['#1976D2', '#D32F2F'],
                                    'Heart Rate History',
                                    'bpm'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
                # Sleep history
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Sleep History", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_history_line_chart(
                                    df_history,
                                    ['sleep_hours'],
                                    ['Sleep Hours'],
                                    ['#4CAF50'],
                                    'Sleep Hours History',
                                    'hours',
                                    add_range=True,
                                    range_min=7,
                                    range_max=9
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
            ]),
            
            dbc.Row([
                # HRV history
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("HRV History", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_history_line_chart(
                                    df_history,
                                    ['hrv_rest'],
                                    ['HRV'],
                                    ['#673AB7'],
                                    'Heart Rate Variability History',
                                    'ms'
                                ),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
            ]),
            
            # Heart rate zones
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_heart_rate_zones_chart(df_single_day),
                                style={"height": "300px"}
                            )
                        ])
                    ])
                ], width=12, className="mb-4"),
            ]),
        ])
    except Exception as e:
        print(f"Error creating participant detail visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading participant data: {str(e)}", color="danger")
        ])

# Helper functions for creating charts
def create_group_bar_chart(df, x_col, y_col, title, y_label, color):
    """Create a bar chart for group comparison"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        text=df[y_col].round(1),
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Group',
        yaxis_title=y_label,
        margin=dict(l=40, r=40, t=60, b=40),
        template='plotly_white'
    )
    
    return fig

def create_participant_bar_chart(df, x_col, y_cols, names, colors, title, y_label):
    """Create a bar chart comparing participants for one or more metrics"""
    fig = go.Figure()
    
    grouped_df = df.groupby(x_col)[y_cols].mean().reset_index()
    
    # Add a trace for each metric
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=grouped_df[x_col],
            y=grouped_df[y_col],
            name=names[i],
            marker_color=colors[i],
            text=grouped_df[y_col].round(1),
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Participant',
        yaxis_title=y_label,
        barmode='group',
        margin=dict(l=40, r=40, t=60, b=60),
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_history_line_chart(df, y_cols, names, colors, title, y_label, add_range=False, range_min=None, range_max=None):
    """Create a line chart showing historical data"""
    fig = go.Figure()
    
    # Add a trace for each metric
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[y_col],
            mode='lines+markers',
            name=names[i],
            line=dict(color=colors[i], width=2),
            marker=dict(size=6)
        ))
    
    # Add recommended range if specified
    if add_range and range_min is not None and range_max is not None:
        fig.add_shape(
            type="rect",
            x0=df['date'].min(),
            x1=df['date'].max(),
            y0=range_min,
            y1=range_max,
            fillcolor="rgba(0,200,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        fig.add_annotation(
            x=df['date'].max(),
            y=(range_min + range_max) / 2,
            text="Recommended Range",
            showarrow=False,
            font=dict(size=10, color="green")
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=y_label,
        margin=dict(l=40, r=40, t=60, b=40),
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Format x-axis dates
    fig.update_xaxes(
        tickformat="%b %d",
        tickangle=-45
    )
    
    return fig

def create_dual_axis_chart(df, x_col, y1_col, y2_col, y1_name, y2_name, y1_color, y2_color, title):
    """Create a chart with dual y-axes"""
    fig = go.Figure()
    
    # Add bars for first metric
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y1_col],
        name=y1_name,
        marker_color=y1_color,
        yaxis='y'
    ))
    
    # Add line for second metric
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        name=y2_name,
        mode='lines+markers',
        line=dict(color=y2_color, width=2),
        marker=dict(size=6),
        yaxis='y2'
    ))
    
    # Update layout for dual axis
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Date",
            tickformat="%b %d",
            tickangle=-45
        ),
        yaxis=dict(
            title=y1_name,
            titlefont=dict(color=y1_color),
            tickfont=dict(color=y1_color)
        ),
        yaxis2=dict(
            title=y2_name,
            titlefont=dict(color=y2_color),
            tickfont=dict(color=y2_color),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        margin=dict(l=60, r=60, t=60, b=60),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_heart_rate_zones_chart(df):
    """Create a pie chart showing heart rate zone distribution"""
    # Extract zone columns
    zone_cols = [f'zone{i}_percent' for i in range(1, 8)]
    
    # Check if we have zone data
    if not all(col in df.columns for col in zone_cols):
        # Create empty chart with message
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text="No heart rate zone data available",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=300
        )
        return fig
    
    # Get zone percentages (use first row if multiple days)
    zone_data = df[zone_cols].iloc[0]
    
    # Create zone labels
    zone_labels = [f"Zone {i}" for i in range(1, 8)]
    
    # Create zone descriptions
    zone_desc = {
        'Zone 1': 'Very Light (50-60% Max HR)',
        'Zone 2': 'Light (60-70% Max HR)',
        'Zone 3': 'Moderate (70-80% Max HR)',
        'Zone 4': 'Hard (80-90% Max HR)',
        'Zone 5': 'Very Hard (90-100% Max HR)',
        'Zone 6': 'Anaerobic (100-110% Max HR)',
        'Zone 7': 'Maximal (110%+ Max HR)'
    }
    
    # Create hover text
    hover_text = [f"{label}: {zone_data[i]:.1f}%<br>{zone_desc[label]}" 
                 for i, label in enumerate(zone_labels)]
    
    # Colors for zones
    colors = ["#80d8ff", "#4dd0e1", "#26c6da", "#26a69a", "#9ccc65", "#ffee58", "#ffab91"]
    
    # Create chart
    fig = go.Figure()
    
    # Add pie chart
    fig.add_trace(go.Pie(
        labels=zone_labels,
        values=zone_data,
        text=[zone_desc[label] for label in zone_labels],
        hovertext=hover_text,
        textinfo='label+percent',
        marker=dict(colors=colors),
        hole=0.3
    ))
    
    # Update layout
    fig.update_layout(
        title="Heart Rate Zone Distribution",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig

# Toggle mock data form
@callback(
    Output("mock-data-collapse", "is_open"),
    Input("generate-mock-data-btn", "n_clicks"),
    State("mock-data-collapse", "is_open")
)
def toggle_mock_data_form(n_clicks, is_open):
    """Toggle the mock data form"""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("generate-data-status", "children"),
    Input("confirm-generate-data-btn", "n_clicks"),
    [State("group-dropdown", "value"),
     State("mock-data-start-date", "date"),
     State("mock-data-end-date", "date"),
     State("overwrite-data-checkbox", "value")],
    prevent_initial_call=True
)
def generate_mock_data(n_clicks, group_id, start_date, end_date, overwrite):
    """Generate mock data for the selected group"""
    if not n_clicks:
        raise PreventUpdate
    
    from utils.database import import_mock_data, get_participants_by_group
    
    try:
        # Convert overwrite checkbox value
        overwrite_data = 1 in overwrite if overwrite else False
        
        if not group_id:
            return html.Div("Please select a group first", style={"color": "red"})
            
        # Get all participants in the group
        groups = get_participants_by_group(group_id)
        if not groups or group_id not in groups:
            return html.Div("No participants in the selected group", style={"color": "red"})
        
        participants = groups[group_id]['participants']
        
        if not participants:
            return html.Div("No participants in the selected group", style={"color": "red"})
        
        # Generate data for the first participant
        participant_id = participants[0]["id"]
        success = import_mock_data(participant_id, start_date, end_date, overwrite_data)
        
        if success:
            return html.Div("Data generated successfully!", style={"color": "green"})
        else:
            return html.Div("Error generating data", style={"color": "red"})
    except Exception as e:
        print(f"Error generating mock data: {e}")
        return html.Div(f"Error: {str(e)}", style={"color": "red"})