from dash import html
import dash_bootstrap_components as dbc 
import pandas as pd

def create_daily_snapshot_card(df: pd.DataFrame, questionnaire_df: pd.DataFrame, selected_date: str) -> dbc.Card:
    """
    Create a daily snapshot card with health metrics and questionnaire data
    Args:
        df (DataFrame): Data containing health metrics for the selected date
        questionnaire_df (DataFrame): Data containing questionnaire responses for the selected date
        selected_date (str): The date for which the snapshot is created
        
    Returns:
        A Dash component representing the daily snapshot card
    """
    
    # Check if we have questionnaire data for this date
    has_questionnaire = not questionnaire_df.empty and len(questionnaire_df) > 0
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"Health Metrics for {selected_date}", className="mb-0"),
            html.P("Complete health overview for the selected day", className="text-muted small mb-0 mt-1")
        ]),
        dbc.CardBody([
            # Health Metrics Section
            html.H6("📊 Objective Metrics", className="section-subtitle mb-3"),
            
            # Primary Metrics Row - Health Data
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
                
                dbc.Col([
                    html.Div([
                        html.H3(f"{df['step_count'].iloc[0]:,}", className="text-warning text-center metric-value mb-1"),
                        html.P("Steps", className="text-center small mb-0"),
                        html.P("(count)", className="text-center text-muted extra-small"),
                    ], className="metric-box")
                ], xs=12, md=2, className="mb-3"),
            ], className="g-3"),
            
            # Questionnaire Section
            html.Hr(className="my-4"),
            html.H6("🧠 Subjective Assessment", className="section-subtitle mb-3"),
            
            # Questionnaire Metrics Row
            _create_questionnaire_section(questionnaire_df, has_questionnaire),
            
            # Additional insights row - Updated to include questionnaire insights
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


def _create_questionnaire_section(questionnaire_df: pd.DataFrame, has_questionnaire: bool):
    """Helper function to create the questionnaire section"""
    
    if not has_questionnaire:
        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "No questionnaire data available for this date. Consider adding daily self-assessment data."
            ], color="warning", className="mb-3"),
        ])
    
    # Get the questionnaire data for the day
    q_data = questionnaire_df.iloc[0]
    
    # Helper function to get color based on scale (1-10, where higher is generally better except for fatigue)
    def get_quality_color(value, reverse=False):
        if pd.isna(value):
            return "text-muted"
        if reverse:  # For fatigue - lower is better
            return "text-success" if value <= 30 else "text-warning" if value <= 60 else "text-danger"
        else:  # For sleep quality and motivation - higher is better
            return "text-danger" if value <= 30 else "text-warning" if value <= 60 else "text-success"
    
    def get_quality_text(value, metric_type):
        if pd.isna(value):
            return "No data"
        
        if metric_type == "fatigue":
            if value <= 30: 
                return "Low"
            elif value <= 60: 
                return "Moderate" 
            else: 
                return "High"
        else:  # sleep_quality, motivation
            if value <= 30: 
                return "Poor"
            elif value <= 60: 
                return "Fair"
            else: 
                return "Good"
    
    return dbc.Row([
        # Sleep Quality
        dbc.Col([
            html.Div([
                html.H3(
                    f"{q_data['perceived_sleep_quality']:.0f}/100" if pd.notna(q_data['perceived_sleep_quality']) else "—", 
                    className=f"{get_quality_color(q_data['perceived_sleep_quality'])} text-center metric-value mb-1"
                ),
                html.P("Sleep Quality", className="text-center small mb-0"),
                html.P(f"({get_quality_text(q_data['perceived_sleep_quality'], 'sleep_quality')})", className="text-center text-muted extra-small"),
            ], className="metric-box")
        ], xs=6, md=4, className="mb-3"),
        
        # Fatigue Level
        dbc.Col([
            html.Div([
                html.H3(
                    f"{q_data['fatigue_level']:.0f}/100" if pd.notna(q_data['fatigue_level']) else "—", 
                    className=f"{get_quality_color(q_data['fatigue_level'], reverse=True)} text-center metric-value mb-1"
                ),
                html.P("Fatigue Level", className="text-center small mb-0"),
                html.P(f"({get_quality_text(q_data['fatigue_level'], 'fatigue')})", className="text-center text-muted extra-small"),
            ], className="metric-box")
        ], xs=6, md=4, className="mb-3"),
        
        # Motivation Level
        dbc.Col([
            html.Div([
                html.H3(
                    f"{q_data['motivation_level']:.0f}/100" if pd.notna(q_data['motivation_level']) else "—", 
                    className=f"{get_quality_color(q_data['motivation_level'])} text-center metric-value mb-1"
                ),
                html.P("Motivation", className="text-center small mb-0"),
                html.P(f"({get_quality_text(q_data['motivation_level'], 'motivation')})", className="text-center text-muted extra-small"),
            ], className="metric-box")
        ], xs=12, md=4, className="mb-3"),
    ], className="g-3")