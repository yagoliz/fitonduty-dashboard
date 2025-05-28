from dash import html, dcc
import dash_bootstrap_components as dbc
from utils.visualization import create_history_line_chart, create_heart_rate_zones_chart

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
            dbc.Alert("No data available for the selected participant and date range", color="warning")
        ])
    
    title_prefix = f"{participant_name}'s" if participant_name else "Participant"
    
    return html.Div([
        # Summary cards
        dbc.Row([
            # Heart rate card
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{df_single_day['resting_hr'].iloc[0]:.0f}", className="card-title text-center text-primary"),
                        html.P("Resting Heart Rate (bpm)", className="card-text text-center"),
                    ])
                ], color="light", outline=True)
            ], className="mb-5"),

            # Max HR card
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{df_single_day['max_hr'].iloc[0]:.0f}", className="card-title text-center text-danger"),
                        html.P("Max Heart Rate (bpm)", className="card-text text-center"),
                    ])
                ], color="light", outline=True)
            ], className="mb-5"),
            
            # Sleep card
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{df_single_day['sleep_hours'].iloc[0]:.1f}", className="card-title text-center text-success"),
                        html.P("Sleep Hours", className="card-text text-center"),
                    ])
                ], color="light", outline=True)
            ], className="mb-5"),
            
            # HRV card
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{df_single_day['hrv_rest'].iloc[0]:.0f}", className="card-title text-center text-info"),
                        html.P("HRV (ms)", className="card-text text-center"),
                    ])
                ], color="light", outline=True)
            ], className="mb-5"),

            # Step count card
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{df_single_day['step_count'].iloc[0]:.0f}", className="card-title text-center text-warning"),
                        html.P("Steps ", className="card-text text-center"),
                    ])
                ], color="light", outline=True)
            ], className="mb-5"),
        ]),

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
                                figure=create_history_line_chart(
                                    df_history,
                                    ['resting_hr', 'max_hr'],
                                    ['Resting HR', 'Max HR'],
                                    ['#1976D2', '#D32F2F'],
                                    'Heart Rate History',
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
            
            # Sleep history
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} Sleep History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_history_line_chart(
                                    df_history,
                                    ['sleep_hours'],
                                    ['Sleep Hours'],
                                    ['#4CAF50'],
                                    'Sleep Hours History',
                                    'hours',
                                    add_range=True,
                                    range_min=7,
                                    range_max=9
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
        
        dbc.Row([
            # HRV history
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} HRV History", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_history_line_chart(
                                    df_history,
                                    ['hrv_rest'],
                                    ['HRV'],
                                    ['#673AB7'],
                                    'Heart Rate Variability History',
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
            
            # Heart rate zones
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(f"{title_prefix} Heart Rate Zones", className="card-title")),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                figure=create_heart_rate_zones_chart(df_single_day),
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