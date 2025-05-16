from datetime import datetime, timedelta

from dash import callback, Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

from components.admin.group_comparison import create_group_comparison
from components.admin.group_summary import create_group_summary
from components.admin.participant_detail import create_participant_detail

from utils.database import (
    get_participants_by_group,
    get_all_groups,
    load_participant_data,
    load_anomaly_data,
    get_user_by_id,
)

from utils.visualization import create_empty_chart, create_anomaly_timeline, create_anomaly_heatmap

@callback(
    [Output("sidebar-column", "className"),
     Output("main-content-column", "className"),
     Output("sidebar-state", "data"),
     Output("sidebar-toggle", "children")],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar-state", "data")],
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, sidebar_state):
    """Toggle the sidebar visibility and update the toggle icon"""
    if not n_clicks:
        raise PreventUpdate
        
    # Get current state
    is_open = sidebar_state.get("is_open", True)
    
    # Toggle state
    is_open = not is_open
    
    # Set appropriate classes based on state
    if is_open:
        # Sidebar is open
        sidebar_class = "sidebar-column px-0"
        content_class = "main-content-column"
        toggle_text = "❮"  # Left arrow when sidebar is open (to close it)
    else:
        # Sidebar is closed
        sidebar_class = "sidebar-column px-0 sidebar-collapsed"
        content_class = "main-content-column"
        toggle_text = "❯"  # Right arrow when sidebar is closed (to open it)
    
    # Update state
    new_state = {"is_open": is_open}
    
    return sidebar_class, content_class, new_state, toggle_text


# Callback to update admin user info
@callback(Output("admin-user-info", "children"), Input("url", "pathname"))
def update_admin_user_info(pathname):
    from flask_login import current_user

    """Update admin user info display"""
    if current_user.is_authenticated and current_user.is_admin:
        return [
            html.H5(current_user.display_name, className="mb-0"),
            html.P("Administrator", className="text-muted"),
        ]
    return html.P("Not logged in")


# Callback to populate the group dropdown
@callback(
    Output("group-dropdown", "options"),
    Output("group-dropdown", "value"),
    Input("url", "pathname"),
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
    [Input("group-dropdown", "value"), Input("show-all-checkbox", "value")],
    prevent_initial_call=True,
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

        participants = groups[selected_group]["participants"]

        if not participants:
            return html.Div("No participants in the selected group")

        # Create dropdown component
        return html.Div(
            [
                html.Label("Participant"),
                dcc.Dropdown(
                    id="participant-dropdown",
                    options=[
                        {"label": participant["username"], "value": participant["id"]}
                        for participant in participants
                    ],
                    value=participants[0]["id"] if participants else None,
                    clearable=False,
                ),
            ]
        )
    except Exception as e:
        print(f"Error updating participant dropdown: {e}")
        return html.Div(f"Error loading participants: {str(e)}")


# Callback to store the selected participant ID
@callback(
    Output("selected-participant-store", "data"),
    [Input("participant-dropdown", "value"), Input("show-all-checkbox", "value")],
    [State("group-dropdown", "value")],
    prevent_initial_call=True,
)
def update_participant_store(participant_id, show_all, group_id):
    """Store the selected participant ID"""
    if 1 in show_all or not group_id:
        return None

    if participant_id:
        return participant_id

    # If participant_id is None but we should have one, try to get the first participant
    if group_id:
        try:
            groups = get_participants_by_group(group_id)
            if group_id in groups and groups[group_id]["participants"]:
                return groups[group_id]["participants"][0]["id"]
        except Exception as e:
            print(f"Error getting first participant: {e}")

    return None


# Callback to update the selected view info
@callback(
    Output("selected-view-info", "children"),
    [
        Input("group-dropdown", "value"),
        Input("selected-participant-store", "data"),
        Input("show-all-checkbox", "value"),
        Input("admin-date-range", "data"),
    ]
)
def update_selected_view_info(group_id, participant_id, show_all, date_range):
    """Update the information about what data is being displayed"""

    # Handle date range display text
    date_info = ""
    if date_range:
        start_date = date_range.get("start_date")
        end_date = date_range.get("end_date")
        
        if start_date and end_date:
            start_str = (
                datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
                if isinstance(start_date, str)
                else start_date.strftime("%b %d, %Y")
            )
            end_str = (
                datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")
                if isinstance(end_date, str)
                else end_date.strftime("%b %d, %Y")
            )
            
            # Check if it's a single day
            if start_date == end_date:
                date_info = f"on {end_str}"
            else:
                date_info = f"from {start_str} to {end_str}"

    if 1 in show_all:
        return html.Div([
            html.H4(f"Viewing: All Participants {date_info}"),
            html.P("Displaying aggregated data across all groups and participants."),
        ])

    if not group_id:
        return html.Div("Please select a group")

    try:
        # Get group name
        groups = get_all_groups()
        group_name = next(
            (g["name"] for g in groups if g["id"] == group_id), f"Group {group_id}"
        )

        if not participant_id:
            return html.Div([
                html.H4(f"Viewing: {group_name} {date_info}"),
                html.P("Please select a participant or choose 'Show all participants'."),
            ])

        # Get participant name
        participant_groups = get_participants_by_group(group_id)
        if group_id in participant_groups:
            participants = participant_groups[group_id]["participants"]
            participant_name = next(
                (p["username"] for p in participants if p["id"] == participant_id),
                f"Participant {participant_id}",
            )
        else:
            # Try to get participant name from user_by_id
            user_data = get_user_by_id(participant_id)
            if user_data:
                participant_name = user_data.get("username", f"Participant {participant_id}")
            else:
                participant_name = f"Participant {participant_id}"

        return html.Div([
            html.H4(f"Viewing: {participant_name} {date_info}"),
            html.P(f"Individual data for participant in {group_name}."),
        ])
    except Exception as e:
        print(f"Error updating view info: {str(e)}")
        return html.Div(f"Error: {str(e)}")


# Callback to update data visualizations
@callback(
    Output("admin-data-visualizations", "children"),
    [
        Input("group-dropdown", "value"),
        Input("show-all-checkbox", "value"),
        Input("selected-participant-store", "data"),
        Input("admin-date-range", "data"),
    ]
)
def update_data_visualizations(group_id, show_all, participant_id, date_range):
    """Update the data visualizations based on selection"""
    if not date_range:
        return html.Div([dbc.Alert("Please select a date range.", color="info")])

    # Extract date information
    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")
    
    if not start_date or not end_date:
        # Default to last 7 days if dates are missing
        today = datetime.now().date()
        end_date = today.isoformat()
        start_date = (today - timedelta(days=6)).isoformat()

    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # If showing all participants
    if 1 in show_all:
        # Return group comparison visualizations
        return create_group_comparison_data(start_date, end_date, "range")

    # If only group is selected
    if group_id and not participant_id:
        # Return group summary visualizations
        return create_group_summary_data(group_id, start_date, end_date, "range")

    # If participant is selected
    if participant_id:
        # Return participant detail visualizations
        return create_participant_detail_data(participant_id, start_date, end_date, "range")

    # Default - no selection
    return html.Div([
        dbc.Alert("Please select a group and/or participant to view data.", color="info")
    ])


def create_group_comparison_data(start_date, end_date, mode):
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

            participants = participant_groups[group_id]["participants"]

            # Accumulate data from all participants
            participant_data = []
            for participant in participants:
                # Load data for this participant over the date range
                df = load_participant_data(participant["id"], start_date, end_date)
                if not df.empty:
                    df["participant_id"] = participant["id"]
                    df["group_id"] = group_id
                    df["group_name"] = group["name"]
                    participant_data.append(df)

            # Combine all participant data for this group
            if participant_data:
                group_df = pd.concat(participant_data)

                # Calculate group averages
                avg_data = {
                    "group_id": group_id,
                    "group_name": group["name"],
                    "avg_resting_hr": group_df["resting_hr"].mean(),
                    "avg_max_hr": group_df["max_hr"].mean(),
                    "avg_sleep_hours": group_df["sleep_hours"].mean(),
                    "avg_hrv_rest": group_df["hrv_rest"].mean(),
                    "participant_count": len(participants),
                }
                group_data.append(avg_data)

        # Convert to DataFrame
        group_df = pd.DataFrame(group_data)

        if group_df.empty:
            return html.Div("No data available for the selected date range")

        # Create visualizations
        return create_group_comparison(group_df)
    except Exception as e:
        print(f"Error creating group comparison visualizations: {e}")
        return html.Div(
            [dbc.Alert(f"Error loading group data: {str(e)}", color="danger")]
        )


def create_group_summary_data(group_id, start_date, end_date, mode):
    """Create data for group summary visualizations"""
    try:
        # Get participants in the group
        participant_groups = get_participants_by_group(group_id)

        if group_id not in participant_groups:
            return html.Div("No participants found in this group")

        group_name = participant_groups[group_id]["name"]
        participants = participant_groups[group_id]["participants"]

        if not participants:
            return html.Div("No participants found in this group")

        # Accumulate data from all participants
        participant_data = []
        for participant in participants:
            # Load data for this participant over the date range
            df = load_participant_data(participant["id"], start_date, end_date)
            if not df.empty:
                df["participant_id"] = participant["id"]
                df["participant_name"] = participant["username"]
                participant_data.append(df)

        # Combine all participant data
        if not participant_data:
            return html.Div("No data available for the selected date range")

        group_df = pd.concat(participant_data)

        # Create visualizations
        return create_group_summary(group_df, group_name)
    except Exception as e:
        print(f"Error creating group summary visualizations: {e}")
        return html.Div(
            [dbc.Alert(f"Error loading group data: {str(e)}", color="danger")]
        )


def create_participant_detail_data(participant_id, start_date, end_date, mode):
    """Create data for participant detail visualizations"""
    try:
        # Load participant data
        df_history = load_participant_data(participant_id, start_date, end_date)

        if df_history.empty:
            return html.Div(
                "No data available for the selected participant and date range"
            )

        # For the summary cards, either use the most recent day or averages
        if mode == "single":
            # For single day view, use that day's data
            df_single_day = df_history
        else:
            # For range views, create a summary row with averages
            avg_row = {}
            for col in df_history.columns:
                if col not in ["date", "participant_id", "participant_name"]:
                    avg_row[col] = df_history[col].mean()

            # Create a single-row DataFrame with the averages
            df_single_day = pd.DataFrame([avg_row])

        # Get participant name if available
        try:
            user_data = get_user_by_id(participant_id)
            participant_name = user_data.get("username") if user_data else None
        except Exception as e:
            print(f"Error getting participant name: {e}")
            participant_name = None

        # Create visualizations
        return create_participant_detail(df_single_day, df_history, participant_name)
    except Exception as e:
        print(f"Error creating participant detail visualizations: {e}")
        return html.Div(
            [dbc.Alert(f"Error loading participant data: {str(e)}", color="danger")]
        )


@callback(
    [Output("admin-anomaly-summary", "children"), Output("admin-anomaly-timeline-chart", "figure")],
    [Input("selected-participant-store", "data"), Input("admin-date-range", "data")],
)
def update_admin_anomaly_timeline(participant_id, date_range):
    """Update admin anomaly timeline chart for selected participant"""
    if not participant_id or not date_range:
        empty_fig = create_empty_chart("No participant or date range selected")
        return html.Div("No data available"), empty_fig

    print(f"TIMELINE CALLBACK TRIGGERED - participant_id: {participant_id}, date_range: {date_range}")

    # Extract date info
    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")
    
    if not start_date or not end_date:
        empty_fig = create_empty_chart("Invalid date range")
        return html.Div("No data available"), empty_fig

    try:
        # If both dates are the same, show a single day view
        if start_date == end_date:
            date_to_use = start_date
            df = load_anomaly_data(participant_id, date=date_to_use)
        else:
            # Looking at multiple days, for timeline show just the last day
            df = load_anomaly_data(participant_id, date=end_date)
        
        if df.empty:
            empty_fig = create_empty_chart("No anomaly data available for the selected date")
            return html.Div("No anomaly data available"), empty_fig

        print(f"DataFrame has {len(df)} rows")

        # Calculate summary statistics
        avg_score = df['score'].mean()
        max_score = df['score'].max()
        anomalies = (df['score'] > 0.8).sum()

        # Create summary card
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_score:.3f}", className="text-primary text-center"),
                    html.P("Avg Anomaly Score", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{max_score:.3f}", className="text-danger text-center"),
                    html.P("Max Anomaly Score", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{anomalies}", className="text-warning text-center"),
                    html.P("Potential Anomalies", className="text-muted text-center small"),
                ], width=4),
            ])
        ])

        # Create timeline chart
        fig = create_anomaly_timeline(df)

        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = create_empty_chart(f"Error loading anomaly data: {str(e)}")
        return html.Div(f"Error: {str(e)}"), empty_fig


@callback(
    Output("admin-anomaly-heatmap-chart", "figure"),
    [Input("selected-participant-store", "data"), Input("admin-date-range", "data")],
)
def update_admin_anomaly_heatmap(participant_id, date_range):
    """Update admin anomaly heatmap chart for selected participant"""
    if not participant_id or not date_range:
        return create_empty_chart("No participant or date range selected")

    # Extract date info
    start_date = date_range.get("start_date")
    end_date = date_range.get("end_date")
    
    if not start_date or not end_date:
        return create_empty_chart("Invalid date range")

    try:
        # Load data for date range
        df = load_anomaly_data(participant_id, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return create_empty_chart("No anomaly data available for the selected date range")

        # Create heatmap
        fig = create_anomaly_heatmap(df)

        return fig
    except Exception as e:
        # Return empty chart in case of error
        return create_empty_chart(f"Error loading anomaly data: {str(e)}")