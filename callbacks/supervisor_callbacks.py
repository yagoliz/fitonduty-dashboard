from datetime import datetime, timedelta

from dash import callback, callback_context, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_login import current_user

from components.supervisor.group_view import create_supervisor_group_view, create_group_header
from utils.database import get_supervisor_group_info
from utils.logging_config import get_logger

logger = get_logger(__name__)


@callback(
    Output("supervisor-navbar-collapse", "is_open"),
    [Input("supervisor-navbar-toggler", "n_clicks")],
    [State("supervisor-navbar-collapse", "is_open")],
)
def toggle_supervisor_navbar_collapse(n_clicks, is_open):
    """Toggle the supervisor navbar collapse on mobile"""
    if n_clicks:
        logger.debug(f"Toggling supervisor navbar collapse: {is_open} -> {not is_open}")
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
    logger.debug(f"Updating supervisor date range: n_7={n_7}, n_30={n_30}, n_90={n_90}, end_date={end_date}")
    
    ctx = callback_context
    if not ctx.triggered:
        logger.debug("No trigger context, returning current data")
        return current_data, "primary", "outline-primary", "outline-primary"
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    logger.debug(f"Trigger ID: {trigger_id}")
    
    # Parse end date
    if isinstance(end_date, str):
        new_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        new_end_date = end_date
    
    logger.debug(f"New end date: {new_end_date}")
    
    # Default button colors
    btn_7_color = "outline-primary"
    btn_30_color = "outline-primary"
    btn_90_color = "outline-primary"
    
    # Determine new date range based on trigger and set active button
    if trigger_id == "supervisor-btn-7-days":
        new_start_date = new_end_date - timedelta(days=6)
        btn_7_color = "primary"
        logger.info(f"Set 7-day date range: {new_start_date} to {new_end_date}")
    elif trigger_id == "supervisor-btn-30-days":
        new_start_date = new_end_date - timedelta(days=29)
        btn_30_color = "primary"
        logger.info(f"Set 30-day date range: {new_start_date} to {new_end_date}")
    elif trigger_id == "supervisor-btn-90-days":
        new_start_date = new_end_date - timedelta(days=89)
        btn_90_color = "primary"
        logger.info(f"Set 90-day date range: {new_start_date} to {new_end_date}")
    else:
        # End date picker changed - keep the same lookback period if known
        if current_data:
            current_start = datetime.strptime(current_data["start_date"], "%Y-%m-%d").date()
            current_end = datetime.strptime(current_data["end_date"], "%Y-%m-%d").date()
            lookback_days = (current_end - current_start).days
            new_start_date = new_end_date - timedelta(days=lookback_days)
            
            logger.debug(f"End date picker changed, maintaining {lookback_days} day lookback")
            
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
            logger.debug("No current data, defaulting to 7-day range")
    
    date_range = {
        "start_date": new_start_date.isoformat(),
        "end_date": new_end_date.isoformat()
    }
    
    logger.debug(f"Final date range: {date_range}")
    return date_range, btn_7_color, btn_30_color, btn_90_color


@callback(
    Output("supervisor-group-header", "children"),
    [Input("supervisor-date-range", "data")],
)
def update_supervisor_group_header(date_range_data):
    """Update supervisor group header with current date range"""
    logger.debug(f"Updating supervisor group header with date range: {date_range_data}")
    
    if not current_user.is_authenticated:
        logger.warning("Unauthenticated user attempting to access supervisor group header")
        raise PreventUpdate
    
    if current_user.role != 'supervisor':
        logger.warning(f"User {current_user.id} with role '{current_user.role}' attempting to access supervisor group header")
        raise PreventUpdate
    
    if not date_range_data:
        logger.warning("No date range data provided for group header")
        raise PreventUpdate
    
    try:
        # Get supervisor's group information
        user_id = current_user.id
        group_info = get_supervisor_group_info(user_id)
        
        if not group_info:
            logger.warning(f"No group assigned to supervisor user_id={user_id}")
            return dbc.Alert("No group assigned to your supervisor account.", color="warning")
        
        # Parse dates
        start_date = datetime.strptime(date_range_data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(date_range_data["end_date"], "%Y-%m-%d").date()
        
        logger.debug(f"Creating group header for group '{group_info['group_name']}' with date range: {start_date} to {end_date}")
        
        return create_group_header(group_info, start_date=start_date, end_date=end_date)
        
    except Exception as e:
        logger.error(f"Error updating supervisor group header: {str(e)}", exc_info=True)
        return dbc.Alert(f"Error loading group information: {str(e)}", color="danger")


@callback(
    Output("supervisor-content-container", "children"),
    [Input("supervisor-date-range", "data")],
)
def update_supervisor_content(date_range_data):
    """Update supervisor content based on selected date range"""
    logger.debug(f"Updating supervisor content with date range: {date_range_data}")
    
    if not current_user.is_authenticated:
        logger.warning("Unauthenticated user attempting to access supervisor content")
        raise PreventUpdate
    
    # Check if user has supervisor role
    if current_user.role != 'supervisor':
        logger.warning(f"User {current_user.id} with role '{current_user.role}' attempting to access supervisor content")
        return dbc.Alert(
            "Access denied. Supervisor role required.",
            color="danger"
        )
    
    if not date_range_data:
        logger.warning("No date range data provided")
        raise PreventUpdate
    
    user_id = current_user.id
    start_date = date_range_data.get("start_date")
    end_date = date_range_data.get("end_date")
    
    logger.info(f"Updating supervisor content for user_id={user_id}, date range: {start_date} to {end_date}")
    
    try:
        # Verify supervisor has a group assigned
        logger.debug(f"Verifying group assignment for supervisor user_id={user_id}")
        group_info = get_supervisor_group_info(user_id)
        if not group_info:
            logger.warning(f"No group assigned to supervisor user_id={user_id}")
            return dbc.Alert(
                "No group assigned to your supervisor account. Please contact an administrator.",
                color="warning"
            )
        
        logger.info(f"Supervisor user_id={user_id} accessing group '{group_info['group_name']}' (id={group_info['id']})")
        
        # Create the supervisor group view
        logger.debug("Creating supervisor group view")
        return create_supervisor_group_view(user_id, start_date, end_date)
        
    except Exception as e:
        logger.error(f"Error loading supervisor data for user_id={user_id}: {str(e)}", exc_info=True)
        return dbc.Alert(f"Error loading supervisor data: {str(e)}", color="danger")