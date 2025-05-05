# layouts/components/participant_ranking.py
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
import numpy as np
from utils.data_utils import load_participant_data

def create_participant_ranking_layout():
    """
    Create the layout for displaying participant rankings based on data availability
    
    Returns:
        A dash component with ranking visualizations
    """
    return html.Div([
        dbc.Card([
            dbc.CardHeader(html.H5("Participant Data Engagement Ranking", className="card-title")),
            dbc.CardBody([
                # Filters row
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Data Type:"),
                        dcc.Dropdown(
                            id="ranking-data-type",
                            options=[
                                {"label": "Overall Data Completeness", "value": "overall"},
                                {"label": "Heart Rate Data", "value": "heart_rate"},
                                {"label": "Sleep Data", "value": "sleep"},
                                {"label": "Activity Data", "value": "activity"}
                            ],
                            value="overall",
                            clearable=False
                        )
                    ], width=12, md=6, className="mb-2"),
                    dbc.Col([
                        dbc.Label("Time Period:"),
                        dcc.Dropdown(
                            id="ranking-time-period",
                            options=[
                                {"label": "Last 7 Days", "value": "7_days"},
                                {"label": "Last 30 Days", "value": "30_days"},
                                {"label": "All Time", "value": "all_time"}
                            ],
                            value="7_days",
                            clearable=False
                        )
                    ], width=12, md=6, className="mb-2")
                ], className="mb-3"),
                
                # Ranking chart
                dcc.Graph(id="participant-ranking-chart", config={'displayModeBar': False}),
                
                # Explainer text
                html.Div([
                    html.P([
                        html.Strong("How to interpret: "),
                        "This visualization ranks participants based on data completeness and engagement. ",
                        "Higher scores indicate more consistent data recording and sensor usage."
                    ], className="text-muted small mt-2")
                ])
            ])
        ])
    ])

@callback(
    Output("participant-ranking-chart", "figure"),
    [Input("group-dropdown", "value"),
     Input("ranking-data-type", "value"),
     Input("ranking-time-period", "value"),
     Input("participant-date-picker", "date")]
)
def update_participant_ranking(group_id, data_type, time_period, selected_date):
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
        
        # Simulate data availability metrics for now
        # In a production environment, you would query your database
        # to get actual counts of data points per participant
        
        # Create a DataFrame with simulated data availability scores
        import random
        
        # Use deterministic random for consistent demo
        # Include all input parameters in the seed for varied but reproducible results
        seed_string = f"{group_id}_{data_type}_{time_period}_{selected_date}"
        random.seed(hash(seed_string))
        
        # Create data frame with participant data
        data = []
        for participant_id in participants:
            # Get participant name from USERS dictionary
            participant_name = USERS.get(participant_id).username if participant_id in USERS else participant_id
            
            # Create variables that affect the score based on inputs
            # Base score between 65-95, different for each participant
            base_score = 65 + (hash(participant_id) % 30)  
            
            # Adjust score based on data type
            type_modifier = {
                "overall": 1.0, 
                "heart_rate": 0.9 + (hash(participant_id+data_type) % 20) / 100,
                "sleep": 0.85 + (hash(participant_id+data_type) % 25) / 100,
                "activity": 0.8 + (hash(participant_id+data_type) % 30) / 100
            }
            
            # Adjust score based on time period
            period_modifier = {
                "7_days": 1.0, 
                "30_days": 0.95 - (hash(participant_id+time_period) % 15) / 100,
                "all_time": 0.9 - (hash(participant_id+time_period) % 20) / 100
            }
            
            # Calculate final score with some randomness
            score = base_score * type_modifier.get(data_type, 1.0) * period_modifier.get(time_period, 1.0)
            # Add some noise but keep within 0-100 range
            score = min(max(score + random.uniform(-5, 5), 0), 100)  
            
            # For data breakdown, either show metrics or daily breakdown
            if data_type == "overall":
                # For overall view, show breakdown by data type
                metrics = {
                    "Heart Rate": score * (0.9 + random.uniform(-0.15, 0.15)),
                    "Sleep": score * (0.85 + random.uniform(-0.15, 0.15)),
                    "Activity": score * (0.8 + random.uniform(-0.15, 0.15)),
                    "HRV": score * (0.75 + random.uniform(-0.15, 0.15))
                }
                # Make sure none exceed 100
                for key in metrics:
                    metrics[key] = min(metrics[key], 100)
            else:
                # For specific data types, simulate day-by-day completeness
                daily_pattern = [random.uniform(0.7, 1.0) for _ in range(7)]
                # Normalize to make some participants more consistent than others
                consistency = 0.7 + (hash(participant_id) % 30) / 100
                daily_pattern = [max(d*consistency + (1-consistency)*0.85, 0.5) for d in daily_pattern]
                
                metrics = {
                    f"Day {i+1}": score * daily_pattern[i] for i in range(7)
                }
                # Make sure none exceed 100
                for key in metrics:
                    metrics[key] = min(metrics[key], 100)
            
            # Add to data list
            data.append({
                "participant_id": participant_id,
                "participant_name": participant_name,
                "score": score,
                **metrics
            })
        
        # Create DataFrame and sort by score in descending order
        df = pd.DataFrame(data).sort_values("score", ascending=False)
        
        # Create a horizontal bar chart with plotly
        fig = go.Figure()
        
        # Add bars for each participant
        fig.add_trace(go.Bar(
            x=df["score"],
            y=df["participant_name"],
            orientation='h',
            marker=dict(
                color=df["score"],
                colorscale='Viridis',
                colorbar=dict(title="Score", ticksuffix="%"),
                cmin=0,
                cmax=100
            ),
            text=[f"{x:.1f}%" for x in df["score"]],
            textposition="auto",
            name="Data Score"
        ))
        
        # Determine chart title based on data type and time period
        data_type_label = {
            "overall": "Overall Data", 
            "heart_rate": "Heart Rate Data", 
            "sleep": "Sleep Data", 
            "activity": "Activity Data"
        }.get(data_type, "Data")
        
        time_period_label = {
            "7_days": "Last 7 Days", 
            "30_days": "Last 30 Days", 
            "all_time": "All Time"
        }.get(time_period, "All Time")
        
        # Update layout
        fig.update_layout(
            title=f"Participant Data Engagement: {data_type_label} ({time_period_label})",
            xaxis_title="Data Completeness Score (%)",
            yaxis_title=None,
            yaxis=dict(
                categoryorder='total ascending'
            ),
            xaxis=dict(
                range=[0, 100]
            ),
            margin=dict(l=10, r=10, t=60, b=30),
            template="plotly_white",
            height=400 if len(participants) > 5 else 300  # Adjust height based on number of participants
        )
        
        # Add reference line for average
        avg_score = df["score"].mean()
        fig.add_shape(
            type="line",
            x0=avg_score,
            x1=avg_score,
            y0=-0.5,
            y1=len(df)-0.5,
            line=dict(
                color="rgba(255, 99, 71, 0.7)",
                width=2,
                dash="dash"
            )
        )
        
        # Add annotation for average
        fig.add_annotation(
            x=avg_score,
            y=len(df)-0.5,
            text=f"Average: {avg_score:.1f}%",
            showarrow=False,
            font=dict(
                color="rgba(255, 99, 71, 0.9)"
            ),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(255, 99, 71, 0.7)",
            borderwidth=1
        )
        
        return fig
    except Exception as e:
        print(f"Error creating ranking chart: {e}")
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