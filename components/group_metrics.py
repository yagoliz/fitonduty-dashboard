from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from utils.data_utils import load_participant_data
from dash.exceptions import PreventUpdate

def create_group_metrics_layout():
    """
    Create the layout for displaying group health metrics
    
    Returns:
        A dash component with metrics and charts for group comparison
    """
    return html.Div([
        dbc.Row([
            # Average heart rate metrics card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Group Average Heart Rate", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="group-heart-rate-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
            
            # Average sleep metrics card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Group Average Sleep", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="group-sleep-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            # Heart rate zones comparison chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Zone Distribution", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="group-hr-zones-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
        
        dbc.Row([
            # HRV comparison chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("HRV Comparison", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="group-hrv-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
    ])

@callback(
    Output("group-heart-rate-chart", "figure"),
    [Input("group-dropdown", "value"),
     Input("participant-date-picker", "date")]
)
def update_group_heart_rate_chart(group_id, date):
    from app import USERS
    
    if not group_id:
        return create_empty_chart("Please select a group")
    
    try:
        # Get all participants in the selected group
        participants = [user_id for user_id, user in USERS.items() 
                      if hasattr(user, 'role') and user.role == 'participant' 
                      and hasattr(user, 'group') and user.group == group_id]
        
        if not participants:
            return create_empty_chart("No participants in selected group")
        
        # Collect data for all participants
        all_data = []
        
        for participant_id in participants:
            df = load_participant_data(participant_id, date)
            if not df.empty:
                df['participant_id'] = participant_id
                all_data.append(df)
        
        if not all_data:
            return create_empty_chart("No data available for the selected date")
        
        # Combine all participant data
        combined_df = pd.concat(all_data)
        
        # Calculate average heart rates by participant
        avg_by_participant = combined_df.groupby('participant_id')[['resting_hr', 'max_hr']].mean().reset_index()
        
        # Create chart with two y-axes for resting and max heart rates
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart for resting heart rate
        fig.add_trace(
            go.Bar(
                x=avg_by_participant['participant_id'],
                y=avg_by_participant['resting_hr'],
                name="Resting Heart Rate",
                marker_color='#1976D2',
                text=avg_by_participant['resting_hr'].round(1),
                textposition="auto"
            ),
            secondary_y=False
        )
        
        # Add bar chart for max heart rate
        fig.add_trace(
            go.Bar(
                x=avg_by_participant['participant_id'],
                y=avg_by_participant['max_hr'],
                name="Max Heart Rate",
                marker_color='#D32F2F',
                text=avg_by_participant['max_hr'].round(1),
                textposition="auto"
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title=f"Heart Rate Comparison for Group {group_id}",
            barmode='group',
            margin=dict(l=40, r=40, t=60, b=60),
            height=300,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Resting Heart Rate (bpm)", secondary_y=False)
        fig.update_yaxes(title_text="Max Heart Rate (bpm)", secondary_y=True)
        
        # Update x-axis
        fig.update_xaxes(title_text="Participant")
        
        return fig
    except Exception as e:
        print(f"Error creating heart rate chart: {e}")
        return create_empty_chart(f"Error creating chart: {str(e)}")

@callback(
    Output("group-sleep-chart", "figure"),
    [Input("group-dropdown", "value"),
     Input("participant-date-picker", "date")]
)
def update_group_sleep_chart(group_id, date):
    from app import USERS
    
    if not group_id:
        return create_empty_chart("Please select a group")
    
    try:
        # Get all participants in the selected group
        participants = [user_id for user_id, user in USERS.items() 
                      if hasattr(user, 'role') and user.role == 'participant' 
                      and hasattr(user, 'group') and user.group == group_id]
        
        if not participants:
            return create_empty_chart("No participants in selected group")
        
        # Collect data for all participants
        all_data = []
        
        for participant_id in participants:
            df = load_participant_data(participant_id, date)
            if not df.empty:
                df['participant_id'] = participant_id
                all_data.append(df)
        
        if not all_data:
            return create_empty_chart("No data available for the selected date")
        
        # Combine all participant data
        combined_df = pd.concat(all_data)
        
        # Calculate average sleep by participant
        avg_by_participant = combined_df.groupby('participant_id')['sleep_hours'].mean().reset_index()
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=avg_by_participant['participant_id'],
                y=avg_by_participant['sleep_hours'],
                marker_color='#4CAF50',
                text=avg_by_participant['sleep_hours'].round(1),
                textposition="auto"
            )
        ])
        
        # Add recommended sleep range
        fig.add_shape(
            type="rect",
            x0=-0.5,
            x1=len(participants) - 0.5,
            y0=7,
            y1=9,
            fillcolor="rgba(0,200,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        # Add annotation for recommended range
        fig.add_annotation(
            x=len(participants) - 1,
            y=8,
            text="Recommended Range",
            showarrow=False,
            font=dict(size=10, color="green")
        )
        
        # Update layout
        fig.update_layout(
            title=f"Sleep Hours Comparison for Group {group_id}",
            xaxis_title="Participant",
            yaxis_title="Sleep Hours",
            yaxis_range=[0, max(10, avg_by_participant['sleep_hours'].max() * 1.1)],
            margin=dict(l=40, r=40, t=60, b=60),
            height=300,
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        print(f"Error creating sleep chart: {e}")
        return create_empty_chart(f"Error creating chart: {str(e)}")

@callback(
    Output("group-hr-zones-chart", "figure"),
    [Input("group-dropdown", "value"),
     Input("participant-date-picker", "date")]
)
def update_group_hr_zones_chart(group_id, date):
    from app import USERS
    
    if not group_id:
        return create_empty_chart("Please select a group")
    
    try:
        # Get all participants in the selected group
        participants = [user_id for user_id, user in USERS.items() 
                      if hasattr(user, 'role') and user.role == 'participant' 
                      and hasattr(user, 'group') and user.group == group_id]
        
        if not participants:
            return create_empty_chart("No participants in selected group")
        
        # Collect data for all participants
        all_data = []
        
        for participant_id in participants:
            df = load_participant_data(participant_id, date)
            if not df.empty:
                df['participant_id'] = participant_id
                all_data.append(df)
        
        if not all_data:
            return create_empty_chart("No data available for the selected date")
        
        # Combine all participant data
        combined_df = pd.concat(all_data)
        
        # Calculate average zone percentages by participant
        zone_cols = [f'zone{i}_percent' for i in range(1, 8)]
        avg_by_participant = combined_df.groupby('participant_id')[zone_cols].mean().reset_index()
        
        # Prepare data for stacked bar chart
        fig = go.Figure()
        
        # Colors for zones
        colors = ["#80d8ff", "#4dd0e1", "#26c6da", "#26a69a", "#9ccc65", "#ffee58", "#ffab91"]
        
        # Add traces for each zone
        for i, zone_col in enumerate(zone_cols):
            fig.add_trace(go.Bar(
                x=avg_by_participant['participant_id'],
                y=avg_by_participant[zone_col],
                name=f"Zone {i+1}",
                marker_color=colors[i],
                text=[f"{v:.1f}%" for v in avg_by_participant[zone_col]],
                textposition="inside"
            ))
        
        # Update layout for stacked bars
        fig.update_layout(
            title=f"Heart Rate Zone Distribution for Group {group_id}",
            xaxis_title="Participant",
            yaxis_title="Percentage of Time",
            barmode='stack',
            margin=dict(l=40, r=40, t=60, b=60),
            height=300,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    except Exception as e:
        print(f"Error creating HR zones chart: {e}")
        return create_empty_chart(f"Error creating chart: {str(e)}")

@callback(
    Output("group-hrv-chart", "figure"),
    [Input("group-dropdown", "value"),
     Input("participant-date-picker", "date")]
)
def update_group_hrv_chart(group_id, date):
    from app import USERS
    
    if not group_id:
        return create_empty_chart("Please select a group")
    
    try:
        # Get all participants in the selected group
        participants = [user_id for user_id, user in USERS.items() 
                      if hasattr(user, 'role') and user.role == 'participant' 
                      and hasattr(user, 'group') and user.group == group_id]
        
        if not participants:
            return create_empty_chart("No participants in selected group")
        
        # If no specific date is selected, get the last 7 days for trend
        show_trend = date is None
        
        # Collect data for all participants
        all_data = []
        
        for participant_id in participants:
            df = load_participant_data(participant_id, date)
            if not df.empty:
                # Add participant ID
                df['participant_id'] = participant_id
                # Add participant name (with safety check)
                if participant_id in USERS and hasattr(USERS.get(participant_id), 'username'):
                    df['participant_name'] = USERS.get(participant_id).username
                else:
                    df['participant_name'] = participant_id
                all_data.append(df)
        
        if not all_data:
            return create_empty_chart("No data available for the selected date")
        
        # Combine all participant data
        combined_df = pd.concat(all_data)
        
        if show_trend:
            # Get the last 7 days of data
            last_7_days = combined_df['date'].max() - pd.Timedelta(days=6)
            trend_df = combined_df[combined_df['date'] >= last_7_days]
            
            # Create line chart for HRV trend by participant
            fig = px.line(
                trend_df,
                x='date',
                y='hrv_rest',
                color='participant_name',
                title=f"HRV Trend for Group {group_id} (Last 7 Days)",
                labels={'hrv_rest': 'HRV at Rest (ms)', 'date': 'Date', 'participant_name': 'Participant'},
                markers=True
            )
            
            # Format x-axis dates
            fig.update_xaxes(
                tickformat="%b %d",
                tickangle=-45
            )
            
        else:
            # Create bar chart for single day comparison
            avg_by_participant = combined_df.groupby(['participant_id', 'participant_name'])['hrv_rest'].mean().reset_index()
            
            fig = px.bar(
                avg_by_participant,
                x='participant_name',
                y='hrv_rest',
                title=f"HRV Comparison for Group {group_id} on {date}",
                labels={'hrv_rest': 'HRV at Rest (ms)', 'participant_name': 'Participant'},
                text_auto='.1f',
                color='hrv_rest',
                color_continuous_scale='Viridis'
            )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=40, r=40, t=60, b=60),
            height=300,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    except Exception as e:
        print(f"Error creating HRV chart: {e}")
        return create_empty_chart(f"Error creating chart: {str(e)}")

def create_empty_chart(message):
    """
    Create an empty chart with a message
    
    Args:
        message: Message to display
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    fig.update_layout(
        title=message,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 16
                }
            }
        ],
        height=300
    )
    
    return fig