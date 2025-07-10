from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

def create_heart_rate_summary(df: pd.DataFrame):
    """Create heart rate summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_resting_hr = df["resting_hr"].mean()
    max_hr = df["max_hr"].max()
    min_hr = df["resting_hr"].min()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_resting_hr:.0f}", className="text-primary text-center"),
                html.P("Avg Resting HR", className="text-muted text-center small"),
            ], width=4),
            dbc.Col([
                html.H3(f"{max_hr:.0f}", className="text-danger text-center"),
                html.P("Max HR", className="text-muted text-center small"),
            ], width=4),
            dbc.Col([
                html.H3(f"{min_hr:.0f}", className="text-success text-center"),
                html.P("Min HR", className="text-muted text-center small"),
            ], width=4),
        ])
    ])


def create_sleep_summary(df: pd.DataFrame):
    """Create sleep summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_sleep = df["sleep_hours"].mean()
    min_sleep = df["sleep_hours"].min()
    max_sleep = df["sleep_hours"].max()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_sleep:.1f}", className="text-primary text-center"),
                html.P("Avg Hours", className="text-muted text-center small"),
            ], width=4),
            dbc.Col([
                html.H3(f"{min_sleep:.1f}", className="text-danger text-center"),
                html.P("Min Hours", className="text-muted text-center small"),
            ], width=4),
            dbc.Col([
                html.H3(f"{max_sleep:.1f}", className="text-success text-center"),
                html.P("Max Hours", className="text-muted text-center small"),
            ], width=4),
        ])
    ])


def create_hrv_summary(df: pd.DataFrame):
    """Create HRV summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_hrv = df["hrv_rest"].mean()
    
    # Calculate trend if we have at least 2 data points
    if len(df) > 1:
        first_val = df.iloc[0]["hrv_rest"]
        last_val = df.iloc[-1]["hrv_rest"]
        trend = last_val - first_val
        trend_pct = (trend / first_val) * 100 if first_val > 0 else 0
    else:
        trend = 0
        trend_pct = 0
    
    trend_color = "text-success" if trend > 0 else "text-danger"
    trend_icon = "↑" if trend > 0 else "↓"
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_hrv:.0f}", className="text-primary text-center"),
                html.P("Avg HRV (ms)", className="text-muted text-center small"),
            ], width=6),
            dbc.Col([
                html.H3([f"{trend_icon} {abs(trend_pct):.1f}%"], className=f"{trend_color} text-center"),
                html.P("Trend", className="text-muted text-center small"),
            ], width=6),
        ])
    ])


def create_period_health_summary(df: pd.DataFrame):
    """Create a comprehensive health summary for the period"""
    if df.empty:
        return html.Div("No data available")
    
    # Calculate various statistics
    days_count = len(df)
    avg_resting_hr = df["resting_hr"].mean()
    avg_sleep = df["sleep_hours"].mean()
    avg_hrv = df["hrv_rest"].mean()
    
    # Sleep quality assessment
    good_sleep_days = (df["sleep_hours"] >= 7).sum()
    sleep_quality_pct = (good_sleep_days / days_count) * 100
    
    # HRV consistency (how stable it is)
    hrv_std = df["hrv_rest"].std()
    hrv_consistency = "High" if hrv_std < 10 else "Moderate" if hrv_std < 20 else "Variable"
    
    # Heart rate recovery (difference between max and resting)
    avg_hr_range = (df["max_hr"] - df["resting_hr"]).mean()
    
    return html.Div([
        # Period Overview
        html.H6("Period Overview", className="text-primary mb-3"),
        html.Div([
            html.Strong(f"{days_count} days"), " of data analyzed"
        ], className="mb-3"),
        
        # Key Metrics
        html.H6("Key Metrics", className="text-primary mb-2"),
        html.Div([
            html.Div([
                html.Strong(f"{avg_resting_hr:.0f} bpm"),
                html.Br(),
                html.Small("Avg Resting HR", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                html.Strong(f"{avg_sleep:.1f} hrs"),
                html.Br(),
                html.Small("Avg Sleep", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                html.Strong(f"{avg_hrv:.0f} ms"),
                html.Br(),
                html.Small("Avg HRV", className="text-muted")
            ], className="mb-3"),
        ]),
        
        # Health Insights
        html.H6("Health Insights", className="text-primary mb-2"),
        html.Div([
            html.Div([
                f"{sleep_quality_pct:.0f}% good sleep days",
                html.Br(),
                html.Small("(7+ hours)", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                f"HRV consistency: {hrv_consistency}",
                html.Br(),
                html.Small(f"Std dev: {hrv_std:.1f}", className="text-muted")
            ], className="mb-2"),
            
            html.Div([
                f"Avg HR range: {avg_hr_range:.0f} bpm",
                html.Br(),
                html.Small("Max - Resting", className="text-muted")
            ], className="mb-2"),
        ])
    ])


def create_questionnaire_summary(df: pd.DataFrame):
    """Create questionnaire summary statistics"""
    from dash import html
    import dash_bootstrap_components as dbc
    
    if df.empty:
        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "No questionnaire data available for this period"
            ], color="info", className="mb-0 text-center")
        ])
    
    # Calculate averages
    avg_sleep_quality = df["perceived_sleep_quality"].mean()
    avg_fatigue = df["fatigue_level"].mean()
    avg_motivation = df["motivation_level"].mean()
    
    # Calculate completion rate and trends
    total_days = len(df)
    
    # Simple trend calculation (compare first half vs second half)
    if total_days > 2:
        mid_point = total_days // 2
        first_half_motivation = df.head(mid_point)["motivation_level"].mean()
        second_half_motivation = df.tail(total_days - mid_point)["motivation_level"].mean()
        motivation_trend = second_half_motivation - first_half_motivation
    else:
        motivation_trend = 0
    
    # Determine trend indicator
    trend_icon = "↑" if motivation_trend > 0.5 else "↓" if motivation_trend < -0.5 else "-"
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_sleep_quality:.1f}", className="text-success text-center"),
                html.P("Avg Sleep Quality", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3(f"{avg_fatigue:.1f}", className="text-warning text-center"),
                html.P("Avg Fatigue", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3(f"{avg_motivation:.1f}", className="text-primary text-center"),
                html.P("Avg Motivation", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3([f"{total_days} ", html.Span(trend_icon, style={"fontSize": "0.8em"})], className="text-info text-center"),
                html.P("Days Logged", className="text-muted text-center small"),
            ], width=3),
        ])
    ])