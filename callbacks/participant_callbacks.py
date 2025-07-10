from datetime import datetime, timedelta

from dash import callback, Input, Output, html, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_login import current_user

import pandas as pd

from components import create_daily_snapshot_card
from components.participant.summaries import create_heart_rate_summary, create_hrv_summary, create_sleep_summary, create_questionnaire_summary
from components.participant.participant_ranking import create_participant_ranking
from components.participant.questionnaire_ranking import create_questionnaire_ranking

from utils.database import (
    load_participant_data,
    load_questionnaire_data,
    get_participant_ranking,
    get_all_group_participants_ranking,
    get_all_group_questionnaire_ranking,
    get_group_historical_data,
    get_participant_questionnaire_ranking,
)
from utils.visualization import (
    create_fatigue_motivation_trend_chart,
    create_heart_rate_trend_chart,
    create_heart_rate_zones_chart,
    create_hrv_trend_chart,
    create_movement_speed_chart,
    create_sleep_quality_trend_chart,
    create_sleep_trend_chart,
    create_step_count_trend_chart,
    create_step_count_summary,
    create_ranking_over_time_figure,
)


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
        far_past = datetime(2024, 1, 1).date()
        today = datetime.now().date() # For questionnaire ranking
        
        # Get data consistency ranking
        ranking_data = get_participant_ranking(user_id, far_past, today)
        all_participants_data = get_all_group_participants_ranking(user_id, far_past, today)
        
        # Get questionnaire completion ranking
        questionnaire_ranking_data = get_participant_questionnaire_ranking(user_id, far_past, today)
        all_questionnaire_data = get_all_group_questionnaire_ranking(user_id, far_past, today)
        
        # Get historical data for ranking over time
        df_history = get_group_historical_data(user_id, far_past, today)
        
        # Create ranking over time figure
        ranking_history_fig = None
        if not df_history.empty:
            ranking_history_fig = create_ranking_over_time_figure(
                user_id, 
                df_history, 
                interval='week'
            )
        
        # Create the layout with sections
        return html.Div([
            # SECTION 1: Data Consistency Ranking
            html.Div([
                html.H5("📊 Data Consistency Ranking", className="section-subtitle mb-3"),
                html.P("Your ranking based on physiological data collection completeness", className="text-muted mb-3"),
                html.Div([
                    create_participant_ranking(ranking_data, all_participants_data, ranking_history_fig) if ranking_data else dbc.Alert(
                        "Data consistency ranking not available", color="warning"
                    )
                ])
            ], className="mb-5"),
            
            # Divider
            html.Hr(className="my-4"),
            
            # SECTION 2: Questionnaire Completion Ranking
            html.Div([
                html.H5("📋 Questionnaire Completion Ranking", className="section-subtitle mb-3"),
                html.P("Your ranking based on daily self-assessment questionnaire responses", className="text-muted mb-3"),
                html.Div([
                    create_questionnaire_ranking(questionnaire_ranking_data, all_questionnaire_data) if questionnaire_ranking_data else dbc.Alert(
                        "Questionnaire ranking not available", color="warning"
                    )
                ])
            ], className="mb-5"),
        ])

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
        # Load health data for just this single day
        df = load_participant_data(user_id, selected_date, selected_date)
        
        # Load questionnaire data for this day
        questionnaire_df = load_questionnaire_data(user_id, selected_date, selected_date)

        if df.empty:
            # Create empty state if no health data is available
            df = pd.DataFrame({
                "date": [selected_date],
                "resting_hr": [None],
                "max_hr": [None],
                "hrv_rest": [None],
                "sleep_hours": [None],
                "step_count": [None],
                "walking_minutes": [None],
                "walking_fast_minutes": [None],
                "jogging_minutes": [None],
                "running_minutes": [None],
            })
        
        # Fill NaN values with 0 for metrics that may not be present
        for col in [
            "resting_hr",
            "max_hr",
            "hrv_rest",
            "sleep_hours",
            "step_count",
            "walking_minutes",
            "walking_fast_minutes",
            "jogging_minutes",
            "running_minutes",
        ]:
            df[col] = df[col].astype(float).fillna(0)

        # Create detailed snapshot with charts (updated to include questionnaire data)
        return html.Div([
            # Header for daily snapshot - now includes both health and questionnaire data
            create_daily_snapshot_card(df, questionnaire_df, selected_date),

            # Charts Row (existing charts remain the same)
            dbc.Row([
                # Heart Rate Zones Doughnut Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title mb-0")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    figure=create_heart_rate_zones_chart(df, chart_type='doughnut'),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper", style={"minHeight": "350px"})
                        ])
                    ])
                ], xs=12, md=6, className="mb-4"),
                
                # Movement Speed Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Movement Activity", className="card-title mb-0")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    figure=create_movement_speed_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper", style={"minHeight": "350px"})
                        ])
                    ])
                ], xs=12, md=6, className="mb-4"),
            ])
        ])

    except Exception as e:
        return dbc.Alert(f"Error loading daily snapshot: {str(e)}", color="danger")


# SECTION 3: HEALTH METRICS - Trends over period (Reorganized into 2 rows)
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
        # Load health data for the date range
        df = load_participant_data(user_id, start_date, end_date)
        
        # Load questionnaire data for the same date range
        questionnaire_df = load_questionnaire_data(user_id, start_date, end_date)

        if df.empty:
            health_data = (dbc.Alert(
                "No health data available for the selected period",
                color="warning"
            ))
        else:
            health_data = (dbc.Row([
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
                ], xs=12, lg=6, className="mb-4"),
                
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
                ], xs=12, lg=6, className="mb-4"),
            ]),
            
            # Row 2: Sleep and Steps
            html.H5("Recovery & Activity Metrics", className="section-subtitle mb-3 mt-4"),
            dbc.Row([
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
                ], xs=12, lg=6, className="mb-4"),
                
                # Step Count Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Daily Steps", className="card-title mb-0")),
                        dbc.CardBody([
                            # Summary statistics
                            html.Div([
                                create_step_count_summary(df)
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_step_count_trend_chart(df),
                                    className="chart-container",
                                    config={'displayModeBar': False, 'responsive': True},
                                    style={'width': '100%', 'height': '100%'}
                                )
                            ], className="chart-wrapper")
                        ])
                    ])
                ], xs=12, lg=6, className="mb-4"),
            ]))

        # Create the health metrics component with charts reorganized into 3 rows
        return html.Div([
            # Row 1: Heart Rate and HRV
            html.H5("Cardiovascular Metrics", className="section-subtitle mb-3"),
            *health_data,
            
            # Row 3: Questionnaire Data (NEW)
            html.H5("Subjective Assessment Metrics", className="section-subtitle mb-3 mt-4"),
            dbc.Row([
                # Sleep Quality Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Perceived Sleep Quality", className="card-title mb-0")),
                        dbc.CardBody([
                            # Summary statistics
                            html.Div([
                                create_questionnaire_summary(questionnaire_df) if not questionnaire_df.empty else html.Div("No questionnaire data available")
                            ], className="metrics-summary"),
                            html.Div([
                                dcc.Graph(
                                    figure=create_sleep_quality_trend_chart(questionnaire_df),
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
                                    figure=create_fatigue_motivation_trend_chart(questionnaire_df),
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

    except Exception as e:
        return dbc.Alert(f"Error loading health metrics: {str(e)}", color="danger")


@callback(
    [Output("snapshot-date-picker", "date"),
     Output("trends-end-date-picker", "date"),
     Output("trends-date-range", "data", allow_duplicate=True)],
    Input("url", "pathname"),
    prevent_initial_call=True
)
def initialize_dates_with_user_data(pathname):
    """Initialize date pickers with the user's most recent data date"""
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    # Import here to avoid circular imports
    from utils.database import get_user_latest_data_date
    
    user_id = current_user.id
    latest_date = get_user_latest_data_date(user_id)
    
    # Use latest data date or fall back to current date
    end_date = latest_date if latest_date else datetime.now().date()
    start_date = end_date - timedelta(days=6)  # Default to 7 days for trends
    
    # Return the dates for both pickers and the trends range
    return (
        end_date,  # snapshot date picker
        end_date,  # trends end date picker
        {
            "end_date": end_date.isoformat(),
            "start_date": start_date.isoformat(),
            "days_back": 7
        }
    )


@callback(
    Output("data-availability-info", "children"),
    Input("url", "pathname")
)
def update_data_availability_info(pathname):
    """Update info about data availability"""
    if not current_user.is_authenticated:
        return ""
    
    from utils.database import get_user_latest_data_date
    
    latest_date = get_user_latest_data_date(current_user.id)
    
    if latest_date:
        days_ago = (datetime.now().date() - latest_date).days
        if days_ago == 0:
            return f"✅ Data available through today ({latest_date.strftime('%B %d, %Y')})"
        elif days_ago == 1:
            return f"📊 Most recent data from yesterday ({latest_date.strftime('%B %d, %Y')})"
        else:
            return f"📊 Most recent data from {days_ago} days ago ({latest_date.strftime('%B %d, %Y')})"
    else:
        return "⚠️ No health data found for your account"

