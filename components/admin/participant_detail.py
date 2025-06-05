from dash import html, dcc
import dash_bootstrap_components as dbc

from components import create_daily_snapshot_card
from utils.visualization import create_heart_rate_trend_chart, create_hrv_trend_chart, create_heart_rate_zones_chart, create_sleep_trend_chart, create_step_count_trend_chart

def create_participant_detail(df_single_day, df_history, participant_name=None):
    """
    Create visualizations for a single participant
    
    Args:
        df_single_day: DataFrame with single day data (for summary cards)
        df_history: DataFrame with historical data (for trend charts)
        participant_name: Name of the participant (optional)
        
    Returns:
        A dash component with participant detail visualizations
    """
    if df_single_day.empty:
        return html.Div([
            dbc.Alert("No data available for the selected participant and date", color="warning")
        ])
    
    title_prefix = f"{participant_name}'s" if participant_name else "Participant"
    
    return html.Div([
        # Daily Summary
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_daily_snapshot_card(df_single_day, df_single_day['date'].iloc[0])
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
            html.H4(f"{title_prefix} Anomaly Detection Results", className="mb-3"),
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
        html.H4(f"{title_prefix} Health Activity", className="mb-3"),

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
    ])