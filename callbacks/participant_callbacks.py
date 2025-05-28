# callbacks/participant_callbacks.py - Clean version for 3-section layout
from dash import callback, Input, Output, html, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_login import current_user
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from components.participant.participant_ranking import create_participant_ranking_layout
from utils.database import load_participant_data, get_participant_ranking
from utils.visualization import create_empty_chart, create_heart_rate_zones_chart


# SECTION 1: RANKING - Uses whole dataset
@callback(
    Output("participant-ranking-container", "children"),
    Input("url", "pathname")  # Triggered when page loads
)
def update_participant_ranking_whole_dataset(pathname):
    """Update participant ranking using entire dataset"""
    if not current_user.is_authenticated:
        raise PreventUpdate

    user_id = current_user.id

    try:
        # Get ranking over entire dataset (no date restrictions)
        # We'll use a very wide date range to capture all data
        far_past = datetime(2020, 1, 1).date()
        far_future = datetime(2030, 12, 31).date()
        
        ranking_data = get_participant_ranking(user_id, far_past, far_future)
        
        if not ranking_data:
            return html.Div(
                dbc.Alert("Ranking information not available", color="warning"),
                className="mb-3"
            )
        
        return create_participant_ranking_layout(ranking_data)

    except Exception as e:
        return dbc.Alert(f"Error loading ranking data: {str(e)}", color="danger")


# SECTION 2: DAILY SNAPSHOT - Single day
@callback(
    Output("daily-snapshot-container", "children"),
    Input("snapshot-date-picker", "date")
)
def update_daily_snapshot(selected_date):
    """Update daily snapshot for selected single day"""
    if not current_user.is_authenticated:
        raise PreventUpdate

    user_id = current_user.id

    try:
        # Load data for just this single day
        df = load_participant_data(user_id, selected_date, selected_date)

        if df.empty:
            return dbc.Alert(
                f"No data available for {selected_date}",
                color="warning"
            )

        # Create detailed snapshot card
        return dbc.Card([
            dbc.CardHeader([
                html.H5(f"Health Metrics for {selected_date}", className="mb-0"),
                html.P("Complete health overview for the selected day", className="text-muted small mb-0 mt-1")
            ]),
            dbc.CardBody([
                # Primary Metrics Row
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df['resting_hr'].iloc[0]:.0f}", className="text-primary text-center metric-value mb-1"),
                            html.P("Resting HR", className="text-center small mb-0"),
                            html.P("(bpm)", className="text-center text-muted extra-small"),
                        ], className="metric-box")
                    ], xs=6, md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df['max_hr'].iloc[0]:.0f}", className="text-danger text-center metric-value mb-1"),
                            html.P("Max HR", className="text-center small mb-0"),
                            html.P("(bpm)", className="text-center text-muted extra-small"),
                        ], className="metric-box")
                    ], xs=6, md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df['sleep_hours'].iloc[0]:.1f}", className="text-success text-center metric-value mb-1"),
                            html.P("Sleep", className="text-center small mb-0"),
                            html.P("(hours)", className="text-center text-muted extra-small"),
                        ], className="metric-box")
                    ], xs=6, md=3, className="mb-3"),
                    
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df['hrv_rest'].iloc[0]:.0f}", className="text-info text-center metric-value mb-1"),
                            html.P("HRV", className="text-center small mb-0"),
                            html.P("(ms)", className="text-center text-muted extra-small"),
                        ], className="metric-box")
                    ], xs=6, md=3, className="mb-3"),
                ], className="g-3"),
                
                # Additional insights row
                html.Hr(className="my-3"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("Heart Rate Range", className="text-muted mb-2"),
                            html.P(f"{df['max_hr'].iloc[0] - df['resting_hr'].iloc[0]:.0f} bpm", className="h5 mb-1"),
                            html.Small("Difference between max and resting HR", className="text-muted")
                        ])
                    ], xs=12, md=4, className="mb-2"),
                    
                    dbc.Col([
                        html.Div([
                            html.H6("Sleep Quality", className="text-muted mb-2"),
                            html.P(
                                "Good" if df['sleep_hours'].iloc[0] >= 7 else "Needs Improvement", 
                                className="h5 mb-1 text-success" if df['sleep_hours'].iloc[0] >= 7 else "h5 mb-1 text-warning"
                            ),
                            html.Small("Based on 7+ hours recommendation", className="text-muted")
                        ])
                    ], xs=12, md=4, className="mb-2"),
                    
                    dbc.Col([
                        html.Div([
                            html.H6("Recovery Status", className="text-muted mb-2"),
                            html.P(
                                "Good" if df['hrv_rest'].iloc[0] >= 50 else "Monitor", 
                                className="h5 mb-1 text-success" if df['hrv_rest'].iloc[0] >= 50 else "h5 mb-1 text-info"
                            ),
                            html.Small("Based on HRV levels", className="text-muted")
                        ])
                    ], xs=12, md=4, className="mb-2"),
                ])
            ])
        ], className="shadow-sm")

    except Exception as e:
        return dbc.Alert(f"Error loading daily snapshot: {str(e)}", color="danger")


# SECTION 3: HEALTH METRICS - Trends over period
@callback(
    Output("health-metrics-container", "children"),
    Input("trends-date-range", "data")
)
def update_health_metrics_trends(date_range_data):
    """Update health metrics based on selected date range"""
    if not current_user.is_authenticated or not date_range_data:
        raise PreventUpdate

    user_id = current_user.id
    start_date = date_range_data.get("start_date")
    end_date = date_range_data.get("end_date")

    try:
        # Load data for the date range
        df = load_participant_data(user_id, start_date, end_date)

        if df.empty:
            return dbc.Alert(
                "No data available for the selected period",
                color="warning"
            )

        # Create the health metrics component with charts and summary stats
        return html.Div([
            dbc.Row([
                # Heart Rate Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate", className="card-title mb-0")),
                        dbc.CardBody([
                            # Summary statistics
                            html.Div([
                                create_heart_rate_summary(df)
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_heart_rate_trend_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=4, className="mb-4"),
                
                # Sleep Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Sleep", className="card-title mb-0")),
                        dbc.CardBody([
                            # Summary statistics
                            html.Div([
                                create_sleep_summary(df)
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_sleep_trend_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=4, className="mb-4"),
                
                # HRV Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate Variability", className="card-title mb-0")),
                        dbc.CardBody([
                            # Summary statistics
                            html.Div([
                                create_hrv_summary(df)
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_hrv_trend_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=4, className="mb-4"),
            ])
        ])

    except Exception as e:
        return dbc.Alert(f"Error loading health metrics: {str(e)}", color="danger")


# SECTION 4: DETAILED ANALYSIS - Uses same date range as health metrics
@callback(
    Output("detailed-analysis-container", "children"),
    Input("trends-date-range", "data")
)
def update_detailed_analysis(date_range_data):
    """Update detailed analysis charts based on selected date range"""
    if not current_user.is_authenticated or not date_range_data:
        raise PreventUpdate

    user_id = current_user.id
    start_date = date_range_data.get("start_date")
    end_date = date_range_data.get("end_date")

    try:
        # Load participant data
        df = load_participant_data(user_id, start_date, end_date)

        if df.empty:
            return dbc.Alert("No data available for detailed analysis", color="warning")

        return html.Div([
            dbc.Row([
                # Heart Rate Zones (larger chart)
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate Zones Distribution", className="card-title mb-0")),
                        dbc.CardBody([
                            html.P("Average distribution across your selected period", className="text-muted small mb-3"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_heart_rate_zones_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper", style={"height": "350px", "min-height": "350px"})
                        ])
                    ])
                ], xs=12, md=6, className="mb-4"),
                
                # # Health Metrics Summary
                # dbc.Col([
                #     dbc.Card([
                #         dbc.CardHeader(html.H5("Period Summary", className="card-title mb-0")),
                #         dbc.CardBody([
                #             html.Div([
                #                 create_period_health_summary(df)
                #             ])
                #         ])
                #     ])
                # ], xs=12, md=4, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Health Metrics Correlation", className="card-title mb-0")),
                        dbc.CardBody([
                            html.P("How your metrics relate to each other", className="text-muted small mb-3"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_metrics_correlation_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper", style={"height": "350px", "min-height": "350px"})
                        ])
                    ])
                ], xs=12, md=6, className="mb-4"),
            ]),
        ])

    except Exception as e:
        return dbc.Alert(f"Error loading detailed analysis: {str(e)}", color="danger")


# Helper functions for creating charts
def create_heart_rate_trend_chart(df):
    """Create heart rate trend chart"""
    if df.empty:
        return create_empty_chart("No heart rate data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["resting_hr"],
        mode="lines+markers",
        name="Resting HR",
        line=dict(color="#1976D2", width=2),
        marker=dict(size=6),
    ))
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["max_hr"],
        mode="lines+markers",
        name="Max HR",
        line=dict(color="#D32F2F", width=2, dash="dot"),
        marker=dict(size=6),
    ))
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45)
    fig.update_yaxes(title_text="BPM")
    
    return fig


def create_sleep_trend_chart(df):
    """Create sleep trend chart"""
    if df.empty:
        return create_empty_chart("No sleep data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["sleep_hours"],
        marker_color="#4CAF50",
        text=df["sleep_hours"].round(1),
        textposition="outside",
    ))
    
    # Add recommended sleep range
    fig.add_shape(
        type="rect",
        x0=df["date"].min(),
        x1=df["date"].max(),
        y0=7,
        y1=9,
        fillcolor="rgba(0,200,0,0.1)",
        line=dict(width=0),
        layer="below",
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45)
    fig.update_yaxes(title_text="Hours", range=[0, max(10, df["sleep_hours"].max() * 1.1)])
    
    return fig


def create_hrv_trend_chart(df):
    """Create HRV trend chart"""
    if df.empty:
        return create_empty_chart("No HRV data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["hrv_rest"],
        mode="lines+markers",
        line=dict(color="#673AB7", width=2),
        marker=dict(size=6),
    ))
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45)
    fig.update_yaxes(title_text="HRV (ms)")
    
    return fig


# Summary functions for health metrics
def create_heart_rate_summary(df):
    """Create heart rate summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_resting_hr = df["resting_hr"].mean()
    max_hr = df["max_hr"].max()
    min_hr = df["resting_hr"].min()
    
    return html.Div([
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
        ])
    ])


def create_sleep_summary(df):
    """Create sleep summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_sleep = df["sleep_hours"].mean()
    min_sleep = df["sleep_hours"].min()
    max_sleep = df["sleep_hours"].max()
    
    return html.Div([
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
        ])
    ])


def create_hrv_summary(df):
    """Create HRV summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_hrv = df["hrv_rest"].mean()
    
    # Calculate trend if we have at least 2 data points
    if len(df) > 1:
        first_val = df.iloc[0]["hrv_rest"]
        last_val = df.iloc[-1]["hrv_rest"]
        trend = last_val - first_val
        trend_pct = (trend / first_val) * 100 if first_val > 0 else 0
    else:
        trend = 0
        trend_pct = 0
    
    trend_color = "text-success" if trend > 0 else "text-danger"
    trend_icon = "↑" if trend > 0 else "↓"
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_hrv:.0f}", className="text-primary text-center"),
                html.P("Avg HRV (ms)", className="text-muted text-center small"),
            ], width=6),
            dbc.Col([
                html.H3([f"{trend_icon} {abs(trend_pct):.1f}%"], className=f"{trend_color} text-center"),
                html.P("Trend", className="text-muted text-center small"),
            ], width=6),
        ])
    ])


def create_period_health_summary(df):
    """Create a comprehensive health summary for the period"""
    if df.empty:
        return html.Div("No data available")
    
    # Calculate various statistics
    days_count = len(df)
    avg_resting_hr = df["resting_hr"].mean()
    avg_sleep = df["sleep_hours"].mean()
    avg_hrv = df["hrv_rest"].mean()
    
    # Sleep quality assessment
    good_sleep_days = (df["sleep_hours"] >= 7).sum()
    sleep_quality_pct = (good_sleep_days / days_count) * 100
    
    # HRV consistency (how stable it is)
    hrv_std = df["hrv_rest"].std()
    hrv_consistency = "High" if hrv_std < 10 else "Moderate" if hrv_std < 20 else "Variable"
    
    # Heart rate recovery (difference between max and resting)
    avg_hr_range = (df["max_hr"] - df["resting_hr"]).mean()
    
    return html.Div([
        # Period Overview
        html.H6("Period Overview", className="text-primary mb-3"),
        html.Div([
            html.Strong(f"{days_count} days"), " of data analyzed"
        ], className="mb-3"),
        
        # Key Metrics
        html.H6("Key Metrics", className="text-primary mb-2"),
        html.Div([
            html.Div([
                html.Strong(f"{avg_resting_hr:.0f} bpm"),
                html.Br(),
                html.Small("Avg Resting HR", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                html.Strong(f"{avg_sleep:.1f} hrs"),
                html.Br(),
                html.Small("Avg Sleep", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                html.Strong(f"{avg_hrv:.0f} ms"),
                html.Br(),
                html.Small("Avg HRV", className="text-muted")
            ], className="mb-3"),
        ]),
        
        # Health Insights
        html.H6("Health Insights", className="text-primary mb-2"),
        html.Div([
            html.Div([
                f"{sleep_quality_pct:.0f}% good sleep days",
                html.Br(),
                html.Small("(7+ hours)", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                f"HRV consistency: {hrv_consistency}",
                html.Br(),
                html.Small(f"Std dev: {hrv_std:.1f}", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                f"Avg HR range: {avg_hr_range:.0f} bpm",
                html.Br(),
                html.Small("Max - Resting", className="text-muted")
            ], className="mb-2"),
        ])
    ])


def create_metrics_correlation_chart(df):
    """Create a correlation chart showing relationships between metrics"""
    if df.empty or len(df) < 2:
        return create_empty_chart("Need at least 2 days of data for correlation analysis")
    
    # Calculate correlations
    metrics = ['resting_hr', 'max_hr', 'sleep_hours', 'hrv_rest']
    correlation_data = []
    
    for i, metric1 in enumerate(metrics):
        for j, metric2 in enumerate(metrics):
            if i < j:  # Only upper triangle to avoid duplicates
                corr = np.corrcoef(df[metric1], df[metric2])[0, 1]
                correlation_data.append({
                    'metric1': metric1,
                    'metric2': metric2,
                    'correlation': corr
                })
    
    # Create a scatter plot showing the strongest correlations
    fig = go.Figure()
    
    # Find the strongest correlation to highlight
    if correlation_data:
        strongest_corr = max(correlation_data, key=lambda x: abs(x['correlation']))
        
        fig.add_trace(go.Scatter(
            x=df[strongest_corr['metric1']],
            y=df[strongest_corr['metric2']],
            mode='markers',
            marker=dict(
                color='#1976D2',
                size=8,
                opacity=0.7
            ),
            name=f"{strongest_corr['metric1'].replace('_', ' ').title()} vs {strongest_corr['metric2'].replace('_', ' ').title()}",
            hovertemplate='<b>%{x}</b><br><b>%{y}</b><extra></extra>'
        ))
        
        # Add trendline
        z = np.polyfit(df[strongest_corr['metric1']], df[strongest_corr['metric2']], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df[strongest_corr['metric1']],
            y=p(df[strongest_corr['metric1']]),
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name=f"Correlation: {strongest_corr['correlation']:.2f}",
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=f"Strongest Correlation: {strongest_corr['metric1'].replace('_', ' ').title()} vs {strongest_corr['metric2'].replace('_', ' ').title()}",
            xaxis_title=strongest_corr['metric1'].replace('_', ' ').title(),
            yaxis_title=strongest_corr['metric2'].replace('_', ' ').title(),
        )
    else:
        fig.add_annotation(
            text="Not enough data for correlation analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig