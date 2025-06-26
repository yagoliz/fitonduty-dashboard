from dash import html
import dash_bootstrap_components as dbc 
import pandas as pd

# Summary Card
def create_daily_snapshot_card(df: pd.DataFrame, selected_date: str) -> dbc.Card:
    """
    Create a daily snapshot card with health metrics including step count
    Args:
        df (DataFrame): Data containing health metrics for the selected date
        selected_date (str): The date for which the snapshot is created
        Returns:
        A Dash component representing the daily snapshot card
    """

    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"Health Metrics for {selected_date}", className="mb-0"),
            html.P("Complete health overview for the selected day", className="text-muted small mb-0 mt-1")
        ]),
        dbc.CardBody([
            # Primary Metrics Row - Now includes Step Count
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['resting_hr'].iloc[0]:.0f}", className="text-primary text-center metric-value mb-1"),
                        html.P("Resting HR", className="text-center small mb-0"),
                        html.P("(bpm)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=6, md=2, className="mb-3"),
                
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['max_hr'].iloc[0]:.0f}", className="text-danger text-center metric-value mb-1"),
                        html.P("Max HR", className="text-center small mb-0"),
                        html.P("(bpm)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=6, md=2, className="mb-3"),
                
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['sleep_hours'].iloc[0]:.1f}", className="text-success text-center metric-value mb-1"),
                        html.P("Sleep", className="text-center small mb-0"),
                        html.P("(hours)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=6, md=2, className="mb-3"),
                
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['hrv_rest'].iloc[0]:.0f}", className="text-info text-center metric-value mb-1"),
                        html.P("HRV", className="text-center small mb-0"),
                        html.P("(ms)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=6, md=2, className="mb-3"),
                
                # NEW: Step Count
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['step_count'].iloc[0]:,}", className="text-warning text-center metric-value mb-1"),
                        html.P("Steps", className="text-center small mb-0"),
                        html.P("(count)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=12, md=2, className="mb-3"),
            ], className="g-3"),
            
            # Additional insights row - Updated to include step insights
            html.Hr(className="my-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("Heart Rate Range", className="text-muted mb-2"),
                        html.P(f"{df['max_hr'].iloc[0] - df['resting_hr'].iloc[0]:.0f} bpm", className="h5 mb-1"),
                        html.Small("Difference between max and resting HR", className="text-muted")
                    ])
                ], xs=12, md=3, className="mb-2"),
                
                dbc.Col([
                    html.Div([
                        html.H6("Sleep Quantity", className="text-muted mb-2"),
                        html.P(
                            "Good" if df['sleep_hours'].iloc[0] >= 7 else "Needs Improvement", 
                            className="h5 mb-1 text-success" if df['sleep_hours'].iloc[0] >= 7 else "h5 mb-1 text-warning"
                        ),
                        html.Small("Based on 7+ hours recommendation", className="text-muted")
                    ])
                ], xs=12, md=3, className="mb-2"),
                
                dbc.Col([
                    html.Div([
                        html.H6("Recovery Status", className="text-muted mb-2"),
                        html.P(
                            "Good" if df['hrv_rest'].iloc[0] >= 50 else "Monitor", 
                            className="h5 mb-1 text-success" if df['hrv_rest'].iloc[0] >= 50 else "h5 mb-1 text-info"
                        ),
                        html.Small("Based on HRV levels", className="text-muted")
                    ])
                ], xs=12, md=3, className="mb-2"),
                
                dbc.Col([
                    html.Div([
                        html.H6("Activity Status", className="text-muted mb-2"),
                        html.P(
                            "Active" if df['step_count'].iloc[0] >= 10000 else "Regular", 
                            className="h5 mb-1 text-success" if df['step_count'].iloc[0] >= 10000 else "h5 mb-1 text-warning"
                        ),
                        html.Small("Based on 10,000 steps/day", className="text-muted")
                    ])
                ], xs=12, md=3, className="mb-2"),
            ])
        ])
    ], className="shadow-sm mb-4")