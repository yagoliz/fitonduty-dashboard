from datetime import datetime

from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from components import create_daily_snapshot_card
from utils.formatting import parse_and_format_date
from utils.visualization import (
    create_heart_rate_trend_chart,
    create_hrv_trend_chart,
    create_heart_rate_zones_chart,
    create_sleep_trend_chart,
    create_step_count_trend_chart,
    create_fatigue_motivation_trend_chart,
    create_sleep_quality_trend_chart,
)

def create_participant_detail(df_history: pd.DataFrame, questionnaire_df_history: pd.DataFrame, selected_date: datetime.date, participant_name=None):
    """
    Create visualizations for a single participant
    
    Args:
        df_history: DataFrame with historical data (for trend charts)
        questionnaire_df_history: DataFrame with historical questionnaire data
        participant_name: Name of the participant (optional)
        
    Returns:
        A dash component with participant detail visualizations
    """

    if df_history.empty:
        df_single_day = pd.DataFrame()
    else:
        # Get the data for the last day
        df_single_day = df_history[df_history["date"] == selected_date]
    
    if questionnaire_df_history.empty:
        df_questionnaire_single = pd.DataFrame()
    else:
        # Get the questionnaire data for the last day
        df_questionnaire_single = questionnaire_df_history[questionnaire_df_history["date"] == selected_date]
    
    title_prefix = f"{participant_name}'s" if participant_name else "Participant"

    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    return html.Div([
        # Daily Summary
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_daily_snapshot_card(df_single_day, df_questionnaire_single, selected_date_str)
                ], width=12, lg=6, className="mb-4"),
                
                # Heart Rate Zones Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5(f"{title_prefix} Heart Rate Zones", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    id="admin-heart-rate-zones-chart",
                                    figure=create_heart_rate_zones_chart(df_single_day),
                                    config={
                                        'displayModeBar': False,
                                        'responsive': True
                                    },
                                    style={
                                        'width': '100%',
                                        'height': '100%'
                                    }
                                )
                            ], className="chart-wrapper", style={"height": "300px"})
                        ])
                    ])
                ], width=12, lg=6, className="mb-4")
            ])
        ]),

        # Anomalies
        html.Div([
            html.H4(f"{title_prefix} Anomaly Detection Results", className="section-title mb-3"),
            dbc.Row([
                # Daily anomaly timeline
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Daily Anomaly Timeline", className="card-title")),
                        dbc.CardBody([
                            html.Div(id="admin-anomaly-summary", className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    id="admin-anomaly-timeline-chart", 
                                    className="chart-container",
                                    config={
                                        'displayModeBar': False,
                                        'responsive': True
                                    },
                                    style={
                                        'width': '100%',
                                        'height': '100%'
                                    }
                                )
                            ], className="chart-wrapper", style={"height": "300px"})
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
                # Weekly heatmap
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Weekly Anomaly Heatmap", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    id="admin-anomaly-heatmap-chart", 
                                    className="chart-container",
                                    config={
                                        'displayModeBar': False,
                                        'responsive': True
                                    },
                                    style={
                                        'width': '100%',
                                        'height': '100%'
                                    }
                                )
                            ], className="chart-wrapper", style={"height": "300px"})
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
            ])
        ], className="anomaly-analysis mb-4"),
        
        # Historical Summary
        html.H4(f"{title_prefix} Health Activity", className="section-title mb-3"),

        # Historical charts
        dbc.Row([
            # Heart rate history
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} Heart Rate History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_heart_rate_trend_chart(df_history),
                                config={
                                    'displayModeBar': False,
                                    'responsive': True
                                },
                                className="chart-container",
                                style={"height": "100%", "width": "100%"}
                            )
                        ], className="chart-wrapper", style={"height": "300px"})
                    ])
                ]),
            ], width=12, lg=6, className="mb-4"),    

            # HRV History
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} HRV History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_hrv_trend_chart(df_history),
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
        
        dbc.Row([
            # Sleep Chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} Sleep History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_sleep_trend_chart(
                                    df_history,
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
            
            # Step Count Chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} Step Count History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_step_count_trend_chart(
                                    df_history,
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

        # Questionnaire Data
        html.H4(f"{title_prefix} Questionnaire Data", className="section-subtitle mb-3"),
        dbc.Row([
            # Sleep Quality Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Perceived Sleep Quality", className="card-title mb-0")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    figure=create_sleep_quality_trend_chart(questionnaire_df_history),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=6, className="mb-4"),
                
                # Fatigue & Motivation Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Fatigue & Motivation Levels", className="card-title mb-0")),
                        dbc.CardBody([
                            # Info text
                            html.Div([
                                html.P("Fatigue: Lower is better • Motivation: Higher is better", 
                                      className="text-muted small text-center mb-2")
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_fatigue_motivation_trend_chart(questionnaire_df_history),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=6, className="mb-4"),
        ])

    ])