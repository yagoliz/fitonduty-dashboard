# components/admin/group_comparison.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from utils.visualization import create_group_bar_chart

def create_group_comparison(group_df):
    """
    Create visualizations comparing all groups
    
    Args:
        group_df: DataFrame with group data
        
    Returns:
        A dash component with group comparison visualizations
    """
    if group_df.empty:
        return html.Div("No data available for comparison")
    
    return html.Div([
        # Group comparison cards
        dbc.Row([
            # Resting heart rate comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Average Resting Heart Rate by Group", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_resting_hr', 
                                    'Average Resting Heart Rate by Group',
                                    'bpm',
                                    '#1976D2'
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
                    dbc.CardHeader(html.H5("Average Sleep Hours by Group", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_sleep_hours', 
                                    'Average Sleep Hours by Group',
                                    'hours',
                                    '#4CAF50'
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
        
        # HRV and activity row
        dbc.Row([
            # HRV comparison
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Average HRV by Group", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_group_bar_chart(
                                    group_df, 
                                    'group_name', 
                                    'avg_hrv_rest', 
                                    'Average Heart Rate Variability by Group',
                                    'ms',
                                    '#673AB7'
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
        
        # Group metrics table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Group Summary Metrics", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dbc.Table.from_dataframe(
                                group_df[[
                                    'group_name', 'participant_count', 'avg_resting_hr', 
                                    'avg_sleep_hours', 'avg_hrv_rest'
                                ]].round(1),
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                header={
                                    'group_name': 'Group',
                                    'participant_count': 'Participants',
                                    'avg_resting_hr': 'Avg Resting HR (bpm)',
                                    'avg_sleep_hours': 'Avg Sleep (hrs)',
                                    'avg_hrv_rest': 'Avg HRV (ms)',
                                }
                            )
                        ])
                    ])
                ])
            ], width=12, className="mb-4"),
        ]),
    ])