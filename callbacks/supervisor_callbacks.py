from datetime import datetime, timedelta

from dash import callback, callback_context, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_login import current_user

from components.supervisor.group_view import create_supervisor_group_view
from utils.database import get_supervisor_group_info


@callback(
    Output("supervisor-navbar-collapse", "is_open"),
    [Input("supervisor-navbar-toggler", "n_clicks")],
    [State("supervisor-navbar-collapse", "is_open")],
)
def toggle_supervisor_navbar_collapse(n_clicks, is_open):
    """Toggle the supervisor navbar collapse on mobile"""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    [Output("supervisor-date-range", "data"),
     Output("supervisor-btn-7-days", "color"),
     Output("supervisor-btn-30-days", "color"),
     Output("supervisor-btn-90-days", "color")],
    [Input("supervisor-btn-7-days", "n_clicks"),
     Input("supervisor-btn-30-days", "n_clicks"),
     Input("supervisor-btn-90-days", "n_clicks"),
     Input("supervisor-end-date-picker", "date")],
    [State("supervisor-date-range", "data")],
)
def update_supervisor_date_range(n_7, n_30, n_90, end_date, current_data):
    """Update the supervisor date range based on button clicks or date changes"""
    
    ctx = callback_context
    if not ctx.triggered:
        return current_data, "primary", "outline-primary", "outline-primary"
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Parse end date
    if isinstance(end_date, str):
        new_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        new_end_date = end_date
    
    # Default button colors
    btn_7_color = "outline-primary"
    btn_30_color = "outline-primary"
    btn_90_color = "outline-primary"
    
    # Determine new date range based on trigger and set active button
    if trigger_id == "supervisor-btn-7-days":
        new_start_date = new_end_date - timedelta(days=6)
        btn_7_color = "primary"
    elif trigger_id == "supervisor-btn-30-days":
        new_start_date = new_end_date - timedelta(days=29)
        btn_30_color = "primary"
    elif trigger_id == "supervisor-btn-90-days":
        new_start_date = new_end_date - timedelta(days=89)
        btn_90_color = "primary"
    else:
        # End date picker changed - keep the same lookback period if known
        if current_data:
            current_start = datetime.strptime(current_data["start_date"], "%Y-%m-%d").date()
            current_end = datetime.strptime(current_data["end_date"], "%Y-%m-%d").date()
            lookback_days = (current_end - current_start).days
            new_start_date = new_end_date - timedelta(days=lookback_days)
            
            # Set active button based on lookback period
            if lookback_days == 6:
                btn_7_color = "primary"
            elif lookback_days == 29:
                btn_30_color = "primary"
            elif lookback_days == 89:
                btn_90_color = "primary"
        else:
            # Default to 7 days
            new_start_date = new_end_date - timedelta(days=6)
            btn_7_color = "primary"
    
    return {
        "start_date": new_start_date.isoformat(),
        "end_date": new_end_date.isoformat()
    }, btn_7_color, btn_30_color, btn_90_color


@callback(
    Output("supervisor-content-container", "children"),
    [Input("supervisor-date-range", "data")],
)
def update_supervisor_content(date_range_data):
    """Update supervisor content based on selected date range"""
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    # Check if user has supervisor role
    if current_user.role != 'supervisor':
        return dbc.Alert(
            "Access denied. Supervisor role required.",
            color="danger"
        )
    
    if not date_range_data:
        raise PreventUpdate
    
    user_id = current_user.id
    start_date = date_range_data.get("start_date")
    end_date = date_range_data.get("end_date")
    
    try:
        # Verify supervisor has a group assigned
        group_info = get_supervisor_group_info(user_id)
        if not group_info:
            return dbc.Alert(
                "No group assigned to your supervisor account. Please contact an administrator.",
                color="warning"
            )
        
        # Create the supervisor group view
        return create_supervisor_group_view(user_id, start_date, end_date)
        
    except Exception as e:
        return dbc.Alert(f"Error loading supervisor data: {str(e)}", color="danger")