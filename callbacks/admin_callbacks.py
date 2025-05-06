# callbacks/admin_callbacks.py
from dash import callback, Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta

from utils.database import (
    get_participants_by_group, 
    get_all_groups, 
    load_participant_data,
    import_mock_data
)

from components.admin.group_comparison import create_group_comparison
from components.admin.group_summary import create_group_summary
from components.admin.participant_detail import create_participant_detail

# Callback to update admin user info
@callback(
    Output("admin-user-info", "children"),
    Input("url", "pathname")
)
def update_admin_user_info(pathname):
    from flask_login import current_user
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

# Callback to update data visualizations
@callback(
    Output("admin-data-visualizations", "children"),
    [Input("group-dropdown", "value"),
     Input("show-all-checkbox", "value"),
     Input("admin-date-picker", "date"),
     Input("selected-participant-store", "data")]
)
def update_data_visualizations(group_id, show_all, date, participant_id):
    """Update the data visualizations based on selection"""
    if not date:
        date = datetime.now().date()
    
    # If showing all participants
    if 1 in show_all:
        # Return group comparison visualizations
        return create_group_comparison_data(date)
    
    # If only group is selected
    if group_id and not participant_id:
        # Return group summary visualizations
        return create_group_summary_data(group_id, date)
    
    # If participant is selected
    if participant_id:
        # Return participant detail visualizations
        return create_participant_detail_data(participant_id, date)
    
    # Default - no selection
    return html.Div([
        dbc.Alert("Please select a group and/or participant to view data.", color="info")
    ])


def create_group_comparison_data(date):
    """Create data for group comparison visualizations"""
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
        return create_group_comparison(group_df)
    except Exception as e:
        print(f"Error creating group comparison visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading group data: {str(e)}", color="danger")
        ])

def create_group_summary_data(group_id, date):
    """Create data for group summary visualizations"""
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
        return create_group_summary(group_df, group_name)
    except Exception as e:
        print(f"Error creating group summary visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading group data: {str(e)}", color="danger")
        ])

def create_participant_detail_data(participant_id, date):
    """Create data for participant detail visualizations"""
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
        return create_participant_detail(df_single_day, df_history)
    except Exception as e:
        print(f"Error creating participant detail visualizations: {e}")
        return html.Div([
            dbc.Alert(f"Error loading participant data: {str(e)}", color="danger")
        ])

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
def generate_mock_data_callback(n_clicks, group_id, start_date, end_date, overwrite):
    """Generate mock data for the selected group"""
    if not n_clicks:
        raise PreventUpdate
    
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