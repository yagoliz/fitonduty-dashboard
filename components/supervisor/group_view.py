from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from utils.database import get_num_participants_by_group, get_supervisor_group_data, get_supervisor_group_info
from utils.visualization.supervisor_charts import (
    create_data_count_chart,
    create_dual_axis_physiological_chart,
    create_subjective_metrics_chart,
    create_empty_chart
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


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
    logger.info(f"Creating supervisor group view for user_id={user_id}, start_date={start_date}, end_date={end_date}")
    
    try:
        # Get supervisor's group info
        logger.debug(f"Getting supervisor group info for user_id={user_id}")
        group_info = get_supervisor_group_info(user_id)
        
        if not group_info:
            logger.warning(f"No group assigned to supervisor user_id={user_id} or access denied")
            return html.Div([
                dbc.Alert("No group assigned to supervisor or access denied.", color="warning")
            ])
        
        logger.info(f"Supervisor user_id={user_id} assigned to group: {group_info['group_name']} (id={group_info['id']})")
        
        # Get aggregated data for the group
        logger.debug(f"Getting aggregated data for group_id={group_info['id']} from {start_date} to {end_date}")
        num_participants = get_num_participants_by_group(group_info['id'])
        df = get_supervisor_group_data(user_id, start_date, end_date, num_participants)
        
        if df.empty:
            logger.warning(f"No data available for group '{group_info['group_name']}' during period {start_date} to {end_date}")
            return html.Div([
                dbc.Alert(f"No data available for {group_info['group_name']} during the selected period.", color="info")
            ])
        
        logger.info(f"Retrieved {len(df)} days of data for group '{group_info['group_name']}'")
        logger.debug(f"Data date range: {df['date'].min()} to {df['date'].max()}")
        
        # Log data availability summary
        physio_days = df[df['physio_data_count'] > 0].shape[0]
        questionnaire_days = df[df['questionnaire_data_count'] > 0].shape[0]
        logger.info(f"Data summary: {physio_days} days with physiological data, {questionnaire_days} days with questionnaire data")
        
        # Create the components
        logger.debug("Creating summary cards")
        summary_cards = create_summary_cards(df)
        
        logger.debug("Creating data count charts")
        data_count_charts = create_data_count_charts(df, num_participants=num_participants)
        
        logger.debug("Creating aggregated metrics charts")
        aggregated_metrics_charts = create_aggregated_metrics_charts(df)
        
        logger.info(f"Successfully created supervisor group view for user_id={user_id}")
        
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
        logger.error(f"Error creating supervisor group view for user_id={user_id}: {str(e)}", exc_info=True)
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
    logger.debug("Creating summary cards")
    
    if df.empty:
        logger.warning("No data available for summary cards")
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
    
    logger.debug(f"Summary statistics: total_days={total_days}, avg_physio_participation={avg_physio_participation:.2f}, avg_questionnaire_participation={avg_questionnaire_participation:.2f}")
    logger.debug(f"Physiological averages: HR={avg_resting_hr:.1f}, Sleep={avg_sleep_hours:.1f}, Steps={avg_step_count:.0f}")
    logger.debug(f"Subjective averages: Sleep Quality={avg_sleep_quality:.1f}, Fatigue={avg_fatigue_level:.1f}, Motivation={avg_motivation_level:.1f}")
    
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


def create_data_count_charts(df, num_participants=0):
    """Create charts showing data collection counts over time"""
    logger.debug("Creating data count charts")
    
    if df.empty:
        logger.warning("No data available for data count charts")
        return html.Div([
            dbc.Alert("No data available for data count charts", color="info")
        ])
    
    # Log data availability for charts
    physio_data_points = df[df['physio_data_count'] > 0].shape[0]
    questionnaire_data_points = df[df['questionnaire_data_count'] > 0].shape[0]
    logger.debug(f"Data count chart data: {physio_data_points} days with physio data, {questionnaire_data_points} days with questionnaire data")
    
    # Create charts using visualization functions
    logger.debug("Creating physiological data count chart")
    fig_physio = create_data_count_chart(df, 'physio_data_count', 'Daily Physiological Data Collection', num_participants=num_participants, color='#007bff')
    
    logger.debug("Creating questionnaire data count chart")
    fig_questionnaire = create_data_count_chart(df, 'questionnaire_data_count', 'Daily Questionnaire Completion', num_participants=num_participants, color='#28a745')
    
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
    logger.debug("Creating aggregated metrics charts")
    
    if df.empty:
        logger.warning("No data available for aggregated metrics charts")
        return html.Div([
            dbc.Alert("No data available for aggregated metrics charts", color="info")
        ])
    
    # Log data availability for metrics charts
    physio_metrics_days = df.dropna(subset=['avg_resting_hr', 'avg_sleep_hours'], how='all').shape[0]
    subjective_metrics_days = df.dropna(subset=['avg_sleep_quality', 'avg_fatigue_level', 'avg_motivation_level'], how='all').shape[0]
    logger.debug(f"Metrics chart data: {physio_metrics_days} days with physiological metrics, {subjective_metrics_days} days with subjective metrics")
    
    # Create charts using visualization functions
    logger.debug("Creating dual-axis physiological chart")
    fig_physio = create_dual_axis_physiological_chart(df)
    
    logger.debug("Creating subjective metrics chart")
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