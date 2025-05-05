from dash import html, dcc, callback, Input, Output, no_update
import dash_bootstrap_components as dbc
import dash
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def create_participant_metrics_layout():
    """
    Create the layout for displaying participant health metrics
    
    Returns:
        A dash component with metrics cards and charts
    """
    return html.Div([
        dbc.Row([
            # Heart rate metrics card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Metrics", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="heart-rate-gauges")
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
            
            # Sleep metrics card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Sleep Metrics", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="sleep-metrics")
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            # Heart rate zones chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="heart-rate-zones-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
        
        dbc.Row([
            # HRV trend chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("HRV Trend (7-day)", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="hrv-trend-chart", style={"height": "300px"})
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
    ])

def load_participant_data(participant_id, date=None):
    """
    Load participant data from CSV file
    
    Args:
        participant_id: ID of the participant
        date: Optional date to filter data
        
    Returns:
        Pandas DataFrame with participant data
    """
    # In production, you would load from a database or a specific file for each participant
    # For now, we'll use a mock CSV path
    try:
        # Assume data is in a data directory with participant_id as filename
        file_path = f"data/{participant_id}.csv"
        
        # Check if file exists in the current working directory
        if not os.path.exists(file_path):
            # For development, create a mock dataframe
            return create_mock_data(participant_id)
        
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter by date if provided
            if date:
                date = pd.to_datetime(date).date()
                df = df[df['date'].dt.date == date]
        
        return df
    
    except Exception as e:
        print(f"Error loading data for participant {participant_id}: {e}")
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=[
            'date', 'resting_hr', 'max_hr', 'zone1_percent', 'zone2_percent', 
            'zone3_percent', 'zone4_percent', 'zone5_percent', 'zone6_percent', 
            'zone7_percent', 'sleep_hours', 'hrv_rest'
        ])

def create_mock_data(participant_id):
    """
    Create mock data for development purposes
    
    Args:
        participant_id: ID of the participant
        
    Returns:
        Pandas DataFrame with mock data
    """
    # Create date range for the last 30 days
    end_date = pd.Timestamp.now().date()
    start_date = end_date - pd.Timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create random data based on realistic values
    np.random.seed(int(participant_id.replace('participant', '')) * 100)  # Make it reproducible but different for each participant
    
    # Generate mock data
    data = {
        'date': dates,
        'resting_hr': np.random.randint(55, 75, size=len(dates)),
        'max_hr': np.random.randint(140, 190, size=len(dates)),
        'zone1_percent': np.random.uniform(20, 40, size=len(dates)),
        'zone2_percent': np.random.uniform(15, 30, size=len(dates)),
        'zone3_percent': np.random.uniform(10, 25, size=len(dates)),
        'zone4_percent': np.random.uniform(8, 20, size=len(dates)),
        'zone5_percent': np.random.uniform(5, 15, size=len(dates)),
        'zone6_percent': np.random.uniform(2, 10, size=len(dates)),
        'zone7_percent': np.random.uniform(0, 5, size=len(dates)),
        'sleep_hours': np.random.uniform(5.5, 9, size=len(dates)),
        'hrv_rest': np.random.uniform(30, 70, size=len(dates))
    }
    
    # Ensure zone percentages sum to 100
    for i in range(len(dates)):
        zone_cols = [f'zone{j}_percent' for j in range(1, 8)]
        zone_sum = sum(data[col][i] for col in zone_cols)
        for col in zone_cols:
            data[col][i] = data[col][i] / zone_sum * 100
    
    return pd.DataFrame(data)

@callback(
    Output("heart-rate-gauges", "children"),
    [Input("selected-participant-store", "children"),  # Use the store instead of dropdown
     Input("participant-date-picker", "date")]
)
def update_heart_rate_gauges(participant_id, date):
    if not participant_id:
        return html.P("No participant selected")
    
    try:
        # Load data for the selected participant and date
        df = load_participant_data(participant_id, date)
    except Exception as e:
        print(f"Error loading data for participant {participant_id}: {e}")
        return html.Div([
            html.P("Error loading participant data"),
            html.P(str(e), className="text-danger")
        ])
    
    if df.empty:
        return html.P("No data available for the selected date")
    
    # Get the first row (assuming filtered by date)
    row = df.iloc[0]
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Resting HR", className="text-center"),
                dcc.Graph(
                    figure=create_gauge_figure(
                        row["resting_hr"], 40, 100, "bpm", "Resting HR",
                        [[0, 40, "#40C057"], [40, 60, "#82C91E"], [60, 80, "#FAB005"], [80, 100, "#FD7E14"]]
                    ),
                    config={"displayModeBar": False},
                    style={"height": "200px"}
                )
            ])
        ], width=6),
        dbc.Col([
            html.Div([
                html.H6("Max HR", className="text-center"),
                dcc.Graph(
                    figure=create_gauge_figure(
                        row["max_hr"], 100, 220, "bpm", "Max HR",
                        [[100, 140, "blue"], [140, 170, "green"], [170, 190, "yellow"], [190, 220, "red"]]
                    ),
                    config={"displayModeBar": False},
                    style={"height": "200px"}
                )
            ])
        ], width=6)
    ])

@callback(
    Output("sleep-metrics", "children"),
    [Input("selected-participant-store", "children"),  # Use the store instead of dropdown
     Input("participant-date-picker", "date")]
)
def update_sleep_metrics(participant_id, date):
    if not participant_id:
        return html.P("No participant selected")
    
    # Load data for the selected participant and date
    df = load_participant_data(participant_id, date)
    
    if df.empty:
        return html.P("No data available for the selected date")
    
    # Get the first row (assuming filtered by date)
    row = df.iloc[0]
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Sleep Hours", className="text-center"),
                dcc.Graph(
                    figure=create_gauge_figure(
                        row["sleep_hours"], 0, 12, "hours", "Sleep",
                        [[0, 4, "red"], [4, 6, "yellow"], [6, 9, "green"], [9, 12, "yellow"]]
                    ),
                    config={"displayModeBar": False},
                    style={"height": "200px"}
                )
            ])
        ], width=6),
        dbc.Col([
            html.Div([
                html.H6("HRV at Rest", className="text-center"),
                dcc.Graph(
                    figure=create_gauge_figure(
                        row["hrv_rest"], 0, 100, "ms", "HRV",
                        [[0, 20, "red"], [20, 40, "yellow"], [40, 80, "green"], [80, 100, "blue"]]
                    ),
                    config={"displayModeBar": False},
                    style={"height": "200px"}
                )
            ])
        ], width=6)
    ])

@callback(
    Output("heart-rate-zones-chart", "figure"),
    [Input("selected-participant-store", "children"),  # Use the store instead of dropdown
     Input("participant-date-picker", "date")]
)
def update_heart_rate_zones_chart(participant_id, date):
    if not participant_id:
        return create_empty_chart("Select a participant to view data")
    
    # Load data for the selected participant and date
    df = load_participant_data(participant_id, date)
    
    if df.empty:
        return create_empty_chart("No data available for the selected date")
    
    # Get the first row (assuming filtered by date)
    row = df.iloc[0]
    
    # Extract zone percentages
    zones = ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6", "Zone 7"]
    values = [row[f"zone{i}_percent"] for i in range(1, 8)]
    
    # Create color scale
    colors = ["#80d8ff", "#4dd0e1", "#26c6da", "#26a69a", "#9ccc65", "#ffee58", "#ffab91"]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=zones,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f}%" for v in values],
            textposition="auto"
        )
    ])
    
    fig.update_layout(
        title="Percentage of Time in Each Heart Rate Zone",
        xaxis_title="Heart Rate Zone",
        yaxis_title="Percentage of Time",
        yaxis_range=[0, max(values) * 1.1],  # Add 10% padding above max value
        margin=dict(l=40, r=40, t=40, b=40),
        height=300,
        template="plotly_white"
    )
    
    return fig

@callback(
    Output("hrv-trend-chart", "figure"),
    [Input("selected-participant-store", "children"),  # Use the store instead of dropdown
     Input("participant-date-picker", "date")]
)
def update_hrv_trend_chart(participant_id, date):
    if not participant_id:
        return create_empty_chart("Select a participant to view data")
    
    # Load data for the selected participant
    df = load_participant_data(participant_id)
    
    if df.empty:
        return create_empty_chart("No data available")
    
    # Filter to last 7 days up to the selected date
    if date:
        end_date = pd.to_datetime(date).date()
    else:
        end_date = df['date'].max().date()
    
    start_date = end_date - pd.Timedelta(days=6)
    
    # Filter data to date range
    filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    filtered_df = filtered_df.sort_values('date')
    
    # Create line chart
    fig = go.Figure()
    
    # Add HRV trend line
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['hrv_rest'],
        mode='lines+markers',
        name='HRV at Rest',
        line=dict(color="#1976D2", width=3),
        marker=dict(size=8),
        line_shape='spline'
    ))
    
    # Format dates on x-axis
    fig.update_xaxes(
        tickformat="%b %d",
        tickangle=-45,
        tickmode="array",
        tickvals=filtered_df['date']
    )
    
    fig.update_layout(
        title="HRV at Rest - 7 Day Trend",
        xaxis_title="Date",
        yaxis_title="HRV (ms)",
        margin=dict(l=40, r=40, t=40, b=60),
        height=300,
        template="plotly_white",
        hovermode="x unified"
    )
    
    return fig

def create_gauge_figure(value, min_val, max_val, units, title, color_ranges):
    """
    Create a gauge chart
    
    Args:
        value: Value to display in the gauge
        min_val: Minimum value
        max_val: Maximum value
        units: Units to display
        title: Title of the gauge
        color_ranges: List of [min, max, color] ranges
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add trace for the gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f" {units}"},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [r[0], r[1]], "color": r[2]} for r in color_ranges
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": value
            }
        }
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=200
    )
    
    return fig

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