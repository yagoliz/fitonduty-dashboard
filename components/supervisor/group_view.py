from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from utils.database import get_supervisor_group_data, get_supervisor_group_info
from utils.visualization.supervisor_charts import (
    create_data_count_chart,
    create_dual_axis_physiological_chart,
    create_subjective_metrics_chart,
    create_empty_chart
)


def create_supervisor_group_view(user_id, start_date, end_date):
    """
    Create the supervisor group view with aggregated data and data counts
    
    Args:
        user_id: Supervisor's user ID
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        A dash component with supervisor group visualization
    """
    try:
        # Get supervisor's group info
        group_info = get_supervisor_group_info(user_id)
        
        if not group_info:
            return html.Div([
                dbc.Alert("No group assigned to supervisor or access denied.", color="warning")
            ])
        
        # Get aggregated data for the group
        df = get_supervisor_group_data(user_id, start_date, end_date)
        
        if df.empty:
            return html.Div([
                dbc.Alert(f"No data available for {group_info['group_name']} during the selected period.", color="info")
            ])
        
        # Create the components
        summary_cards = create_summary_cards(df)
        data_count_charts = create_data_count_charts(df)
        aggregated_metrics_charts = create_aggregated_metrics_charts(df)
        
        return html.Div([          
            # Summary cards
            dbc.Row([
                dbc.Col([
                    summary_cards
                ], width=12, className="mb-4"),
            ]),
            
            # Data count charts
            dbc.Row([
                dbc.Col([
                    html.H5("Data Collection Overview", className="section-title text-primary mb-3"),
                    data_count_charts
                ], width=12, className="mb-4", style={"min-height": "350px"}),
            ]),
            
            # Aggregated metrics charts
            dbc.Row([
                dbc.Col([
                    html.H5("Group Average Metrics", className="section-title text-primary mb-3"),
                    aggregated_metrics_charts
                ], width=12, className="mb-4", style={"min-height": "350px"}),
            ]),
        ])
        
    except Exception as e:
        print(f"Error creating supervisor group view: {e}")
        return html.Div([
            dbc.Alert(f"Error loading group data: {str(e)}", color="danger")
        ])


def create_group_header(group_info, start_date, end_date):
    """Create header section with group information"""
    period_text = f"From {start_date} to {end_date}"
    
    return dbc.Card([
        dbc.CardBody([
            html.H4(f"Group: {group_info['group_name']}", className="card-title text-primary"),
            html.P(f"Description: {group_info.get('description', 'No description available')}", className="text-muted"),
            html.P(f"Data Period: {period_text}", className="text-primary"),
        ])
    ], className="mb-4")


def create_summary_cards(df):
    """Create summary cards with key metrics"""
    if df.empty:
        return html.Div("No data available for summary")
    
    # Calculate summary statistics
    total_days = len(df)
    avg_physio_participation = df['physio_data_count'].mean()
    avg_questionnaire_participation = df['questionnaire_data_count'].mean()
    max_physio_participation = df['physio_data_count'].max()
    max_questionnaire_participation = df['questionnaire_data_count'].max()
    
    # Average physiological metrics (excluding null values)
    avg_resting_hr = df['avg_resting_hr'].mean()
    avg_sleep_hours = df['avg_sleep_hours'].mean()
    avg_step_count = df['avg_step_count'].mean()
    
    # Average questionnaire metrics (excluding null values)
    avg_sleep_quality = df['avg_sleep_quality'].mean()
    avg_fatigue_level = df['avg_fatigue_level'].mean()
    avg_motivation_level = df['avg_motivation_level'].mean()
    
    return html.Div([
        # Top row: Data Collection and Participation Rates
        dbc.Row([
            # Data Collection Summary
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Data Collection", className="mb-0"),
                        html.P("Group data availability overview", className="text-muted small mb-0 mt-1")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{total_days}", className="text-primary text-center metric-value mb-1"),
                                    html.P("Days", className="text-center small mb-0"),
                                    html.P("(with data)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_physio_participation:.1f}", className="text-info text-center metric-value mb-1"),
                                    html.P("Avg Physio", className="text-center small mb-0"),
                                    html.P("(per day)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_questionnaire_participation:.1f}", className="text-success text-center metric-value mb-1"),
                                    html.P("Avg Survey", className="text-center small mb-0"),
                                    html.P("(per day)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{max_physio_participation}", className="text-warning text-center metric-value mb-1"),
                                    html.P("Peak", className="text-center small mb-0"),
                                    html.P("(participants)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                        ], className="g-3")
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-4"),
            
            # Participation Rates
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Participation Rates", className="mb-0"),
                        html.P("Group engagement and participation", className="text-muted small mb-0 mt-1")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{(avg_physio_participation/max_physio_participation*100):.0f}%" if max_physio_participation > 0 else "—", className="text-primary text-center metric-value mb-1"),
                                    html.P("Physio Rate", className="text-center small mb-0"),
                                    html.P("(participation)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{(avg_questionnaire_participation/max_questionnaire_participation*100):.0f}%" if max_questionnaire_participation > 0 else "—", className="text-success text-center metric-value mb-1"),
                                    html.P("Survey Rate", className="text-center small mb-0"),
                                    html.P("(participation)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{max(max_physio_participation, max_questionnaire_participation)}", className="text-info text-center metric-value mb-1"),
                                    html.P("Max Group", className="text-center small mb-0"),
                                    html.P("(participants)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=12, className="mb-3"),
                        ], className="g-3")
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-4"),
        ]),
        
        # Bottom row: Physiological Averages and Subjective Averages
        dbc.Row([
            # Physiological Metrics Summary
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Physiological Averages", className="mb-0"),
                        html.P("Group average physiological metrics", className="text-muted small mb-0 mt-1")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_resting_hr:.0f}" if not pd.isna(avg_resting_hr) else "—", className="text-primary text-center metric-value mb-1"),
                                    html.P("Resting HR", className="text-center small mb-0"),
                                    html.P("(bpm)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_sleep_hours:.1f}" if not pd.isna(avg_sleep_hours) else "—", className="text-success text-center metric-value mb-1"),
                                    html.P("Sleep", className="text-center small mb-0"),
                                    html.P("(hours)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_step_count:,.0f}" if not pd.isna(avg_step_count) else "—", className="text-warning text-center metric-value mb-1"),
                                    html.P("Steps", className="text-center small mb-0"),
                                    html.P("(count)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=12, className="mb-3"),
                        ], className="g-3")
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-4"),
            
            # Questionnaire Metrics Summary
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Subjective Averages", className="mb-0"),
                        html.P("Group average subjective assessments", className="text-muted small mb-0 mt-1")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_sleep_quality:.0f}" if not pd.isna(avg_sleep_quality) else "—", className="text-info text-center metric-value mb-1"),
                                    html.P("Sleep Quality", className="text-center small mb-0"),
                                    html.P("(0-100)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_fatigue_level:.0f}" if not pd.isna(avg_fatigue_level) else "—", className="text-danger text-center metric-value mb-1"),
                                    html.P("Fatigue", className="text-center small mb-0"),
                                    html.P("(0-100)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{avg_motivation_level:.0f}" if not pd.isna(avg_motivation_level) else "—", className="text-success text-center metric-value mb-1"),
                                    html.P("Motivation", className="text-center small mb-0"),
                                    html.P("(0-100)", className="text-center text-muted extra-small"),
                                ], className="metric-box")
                            ], xs=12, className="mb-3"),
                        ], className="g-3")
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-4"),
        ])
    ])


def create_data_count_charts(df):
    """Create charts showing data collection counts over time"""
    if df.empty:
        return html.Div([
            dbc.Alert("No data available for data count charts", color="info")
        ])
    
    # Create charts using visualization functions
    fig_physio = create_data_count_chart(df, 'physio_data_count', 'Daily Physiological Data Collection', '#007bff')
    fig_questionnaire = create_data_count_chart(df, 'questionnaire_data_count', 'Daily Questionnaire Completion', '#28a745')
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Physiological Data Collection", className="card-title mb-0")),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(
                            figure=fig_physio,
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
                    ], className="chart-wrapper")
                ])
            ])
        ], xs=12, lg=6, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Questionnaire Completion", className="card-title mb-0")),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(
                            figure=fig_questionnaire,
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
                    ], className="chart-wrapper")
                ])
            ])
        ], xs=12, lg=6, className="mb-4"),
    ])


def create_aggregated_metrics_charts(df):
    """Create charts showing aggregated physiological and questionnaire metrics"""
    if df.empty:
        return html.Div([
            dbc.Alert("No data available for aggregated metrics charts", color="info")
        ])
    
    # Create charts using visualization functions
    fig_physio = create_dual_axis_physiological_chart(df)
    fig_questionnaire = create_subjective_metrics_chart(df)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Physiological Metrics", className="card-title mb-0")),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(
                            figure=fig_physio,
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
                    ], className="chart-wrapper")
                ])
            ])
        ], xs=12, lg=6, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Subjective Assessment Metrics", className="card-title mb-0")),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(
                            figure=fig_questionnaire,
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
                    ], className="chart-wrapper")
                ])
            ])
        ], xs=12, lg=6, className="mb-4"),
    ])