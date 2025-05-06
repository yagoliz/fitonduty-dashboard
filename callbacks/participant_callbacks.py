# callbacks/participant_callbacks.py
from dash import callback, Input, Output, html, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_login import current_user
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.database import load_participant_data
from utils.visualization import create_empty_chart, create_heart_rate_zones_chart

@callback(
    [Output("heart-rate-summary", "children"),
     Output("heart-rate-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_heart_rate_info(start_date, end_date):
    """Update heart rate information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = create_empty_chart("No data available for the selected date range")
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_resting_hr = df['resting_hr'].mean()
        max_hr = df['max_hr'].max()
        min_hr = df['resting_hr'].min()
        
        # Create summary card
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_resting_hr:.0f}", className="text-primary text-center"),
                    html.P("Avg Resting HR", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{max_hr:.0f}", className="text-danger text-center"),
                    html.P("Max HR", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{min_hr:.0f}", className="text-success text-center"),
                    html.P("Min HR", className="text-muted text-center small"),
                ], width=4),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add resting heart rate line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['resting_hr'],
            mode='lines+markers',
            name='Resting HR',
            line=dict(color='#1976D2', width=2),
            marker=dict(size=6)
        ))
        
        # Add max heart rate line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['max_hr'],
            mode='lines+markers',
            name='Max HR',
            line=dict(color='#D32F2F', width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="BPM"
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = create_empty_chart(f"Error loading data: {str(e)}")
        return html.Div("No data available"), empty_fig

@callback(
    [Output("sleep-summary", "children"),
     Output("sleep-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_sleep_info(start_date, end_date):
    """Update sleep information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = create_empty_chart("No data available for the selected date range")
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_sleep = df['sleep_hours'].mean()
        min_sleep = df['sleep_hours'].min()
        max_sleep = df['sleep_hours'].max()
        
        # Create summary card
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_sleep:.1f}", className="text-primary text-center"),
                    html.P("Avg Hours", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{min_sleep:.1f}", className="text-danger text-center"),
                    html.P("Min Hours", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{max_sleep:.1f}", className="text-success text-center"),
                    html.P("Max Hours", className="text-muted text-center small"),
                ], width=4),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add sleep hours bars
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['sleep_hours'],
            marker_color='#4CAF50',
            text=df['sleep_hours'].round(1),
            textposition="outside"
        ))
        
        # Add recommended sleep range
        fig.add_shape(
            type="rect",
            x0=df['date'].min(),
            x1=df['date'].max(),
            y0=7,
            y1=9,
            fillcolor="rgba(0,200,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="Hours",
            range=[0, max(10, max_sleep * 1.1)]
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = create_empty_chart(f"Error loading data: {str(e)}")
        return html.Div("No data available"), empty_fig

@callback(
    [Output("hrv-summary", "children"),
     Output("hrv-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_hrv_info(start_date, end_date):
    """Update HRV information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = create_empty_chart("No data available for the selected date range")
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_hrv = df['hrv_rest'].mean()
        
        # Calculate trend if we have at least 2 data points
        if len(df) > 1:
            first_val = df.iloc[0]['hrv_rest']
            last_val = df.iloc[-1]['hrv_rest']
            trend = last_val - first_val
            trend_pct = (trend / first_val) * 100 if first_val > 0 else 0
        else:
            trend = 0
            trend_pct = 0
        
        # Create summary card
        trend_color = "text-success" if trend > 0 else "text-danger"
        trend_icon = "↑" if trend > 0 else "↓"
        
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_hrv:.0f}", className="text-primary text-center"),
                    html.P("Avg HRV (ms)", className="text-muted text-center small"),
                ], width=6),
                dbc.Col([
                    html.H3([
                        f"{trend_icon} {abs(trend_pct):.1f}%"
                    ], className=f"{trend_color} text-center"),
                    html.P("Trend", className="text-muted text-center small"),
                ], width=6),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add HRV line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['hrv_rest'],
            mode='lines+markers',
            line=dict(color='#673AB7', width=2),
            marker=dict(size=6)
        ))
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="HRV (ms)"
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = create_empty_chart(f"Error loading data: {str(e)}")
        return html.Div("No data available"), empty_fig

@callback(
    Output("heart-rate-zones-chart", "figure"),
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_heart_rate_zones_chart(start_date, end_date):
    """Update heart rate zones chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            return create_empty_chart("No data available for the selected date range")
        
        # Extract zone columns
        zone_cols = [f'zone{i}_percent' for i in range(1, 8)]
        
        # Check if we have zone data
        if not all(col in df.columns for col in zone_cols):
            return create_empty_chart("No heart rate zone data available")
        
        # Calculate average zone values across the date range
        avg_zones = df[zone_cols].mean()
        
        # Create a new dataframe for one row with average values
        avg_df = pd.DataFrame([avg_zones], columns=zone_cols)
        
        # Use the utility function to create the heart rate zones chart
        return create_heart_rate_zones_chart(avg_df)
    except Exception as e:
        # Return empty chart in case of error
        return create_empty_chart(f"Error loading data: {str(e)}")

@callback(
    Output("activity-chart", "figure"),
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_activity_chart(start_date, end_date):
    """Update activity chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            return create_empty_chart("No data available for the selected date range")
        
        # Check if we have steps and other activity data
        if 'steps' in df.columns:
            # Create a figure with dual axis for steps and other metrics
            fig = go.Figure()
            
            # Add steps bars
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['steps'],
                name='Steps',
                marker_color='#3F51B5',
                yaxis='y'
            ))
            
            # Add recovery score line if available
            if 'recovery_score' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['recovery_score'],
                    name='Recovery Score',
                    mode='lines+markers',
                    line=dict(color='#F44336', width=2),
                    marker=dict(size=6),
                    yaxis='y2'
                ))
            
            # Update layout for dual axis
            fig.update_layout(
                title="Daily Activity",
                xaxis=dict(
                    title="Date",
                    tickformat="%b %d",
                    tickangle=-45
                ),
                yaxis=dict(
                    title="Steps",
                    titlefont=dict(color='#3F51B5'),
                    tickfont=dict(color='#3F51B5')
                ),
                yaxis2=dict(
                    title="Recovery Score",
                    titlefont=dict(color='#F44336'),
                    tickfont=dict(color='#F44336'),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    range=[0, 100]
                ),
                margin=dict(l=60, r=60, t=50, b=50),
                height=300,
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            return fig
        else:
            # Create a placeholder chart if activity data isn't available
            fig = go.Figure()
            
            # Update layout with a message
            fig.update_layout(
                title="Activity Metrics",
                margin=dict(l=20, r=20, t=50, b=20),
                height=300,
                template="plotly_white",
                annotations=[
                    dict(
                        text="Activity tracking features coming soon",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=16)
                    )
                ],
                xaxis={"visible": False},
                yaxis={"visible": False}
            )
            
            return fig
            
    except Exception as e:
        # Return empty chart in case of error
        return create_empty_chart(f"Error loading data: {str(e)}")