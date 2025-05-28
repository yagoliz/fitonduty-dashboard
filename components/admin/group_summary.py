# components/admin/group_summary.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from utils.visualization import create_participant_bar_chart

def create_group_summary(group_df, group_name):
    """
    Create visualizations summarizing a single group
    
    Args:
        group_df: DataFrame with participant data for a group
        group_name: Name of the group
        
    Returns:
        A dash component with group summary visualizations
    """
    if group_df.empty:
        return html.Div("No data available for the selected group")
    
    return html.Div([
        # Heart rate and sleep cards
        dbc.Row([
            # Heart rate comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Comparison", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['resting_hr', 'max_hr'],
                                    ['Resting HR', 'Max HR'],
                                    ['#1976D2', '#D32F2F'],
                                    'Heart Rate Comparison',
                                    'bpm'
                                ),
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                className="chart-container",
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-wrapper", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
            
            # Sleep comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Sleep Comparison", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['sleep_hours'],
                                    ['Sleep Hours'],
                                    ['#4CAF50'],
                                    'Sleep Hours Comparison',
                                    'hours'
                                ),
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                className="chart-container",
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-wrapper", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
        ]),
        
        # HRV and Step Count row
        dbc.Row([
            # HRV comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("HRV Comparison", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['hrv_rest'],
                                    ['HRV'],
                                    ['#673AB7'],
                                    'Heart Rate Variability Comparison',
                                    'ms'
                                ),
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                className="chart-container",
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-wrapper", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
            
            # NEW: Step Count comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Daily Steps Comparison", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_participant_bar_chart(
                                    group_df, 
                                    'participant_name', 
                                    ['step_count'],
                                    ['Daily Steps'],
                                    ['#FFA726'],
                                    'Average Daily Steps Comparison',
                                    'steps'
                                ),
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                className="chart-container",
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-wrapper", style={"height": "300px"})
                    ])
                ])
            ], width=12, lg=6, className="mb-4"),
        ]),
        
        # Participant metrics table - Updated to include step count
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"Participant Metrics for {group_name}", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dbc.Table.from_dataframe(
                                group_df[['participant_name', 'resting_hr', 'max_hr', 'sleep_hours', 'hrv_rest', 'step_count']]
                                .groupby('participant_name').mean().reset_index().round(1),
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                header={
                                    'participant_name': 'Participant',
                                    'resting_hr': 'Resting HR (bpm)',
                                    'max_hr': 'Max HR (bpm)',
                                    'sleep_hours': 'Sleep (hrs)',
                                    'hrv_rest': 'HRV (ms)',
                                    'step_count': 'Avg Steps',
                                }
                            )
                        ])
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
    ])