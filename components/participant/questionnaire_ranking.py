from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.visualization import create_questionnaire_race_figure

def create_questionnaire_ranking(ranking_data, all_participants_data=None):
    """
    Create a component showing the participant's questionnaire completion ranking
    
    Args:
        ranking_data: Dictionary with questionnaire ranking information
        all_participants_data: Optional list of all participants' data for race visualization
        
    Returns:
        A dash component showing the questionnaire ranking information
    """
    
    # Calculate percentage for progress bar
    completion_rate = ranking_data.get("completion_rate", 0)
    rank_percentage = (1 - ((ranking_data["rank"] - 1) / ranking_data["total_participants"])) * 100 if ranking_data["total_participants"] > 1 else 100
    
    # Create color based on completion rate
    if completion_rate >= 80:
        rank_color = "success"
        rank_text = "Excellent completion rate! 🌟"
    elif completion_rate >= 60:
        rank_color = "info"
        rank_text = "Good completion rate! 📝"
    elif completion_rate >= 40:
        rank_color = "warning"
        rank_text = "Keep filling those questionnaires! 📊"
    else:
        rank_color = "danger"
        rank_text = "More questionnaires needed! 📋"
    
    # Format questionnaire days display
    questionnaire_days = ranking_data.get("questionnaire_days", 0)
    total_days = ranking_data.get("total_possible_days", 0)
    
    components = []

    campaign_start_date = ranking_data.get("campaign_start_date")
    
    components.append(
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Completion Summary", className="card-title mb-0"),
                    html.Small(
                        f"Campaign period: {campaign_start_date.strftime('%b %d, %Y') if campaign_start_date else 'Not set'} - Present" if campaign_start_date else "Days completed vs. total possible days", 
                        className="text-muted"
                    )
                ]),
                dbc.CardBody([
                    html.Div([
                        # Rank display
                        html.H2(
                            f"{ranking_data['rank']}/{ranking_data['total_participants']}",
                            className=f"text-{rank_color} text-center mb-2"
                        ),
                        html.P(rank_text, className="text-center mb-3"),
                        
                        # Completion rate progress bar
                        html.Div([
                            html.Label(f"Completion Rate: {completion_rate:.1f}%", className="mb-2"),
                            dbc.Progress(
                                value=completion_rate,
                                color=rank_color,
                                className="mb-3",
                                style={"height": "12px"}
                            ),
                        ]),
                        
                        # Days completed with campaign info
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.H4(f"{questionnaire_days}", className="text-primary text-center mb-1"),
                                    html.P("Days Completed", className="text-center small mb-0 text-muted"),
                                ], width=6),
                                dbc.Col([
                                    html.H4(f"{total_days}", className="text-secondary text-center mb-1"),
                                    html.P("Campaign Days", className="text-center small mb-0 text-muted"),
                                ], width=6),
                            ])
                        ]),
                        
                        # Add campaign period info if available
                        html.Div([
                            html.Hr(className="my-2"),
                            html.P([
                                html.I(className="fas fa-calendar-alt me-1"),
                                f"Campaign started: {campaign_start_date.strftime('%B %d, %Y')}" if campaign_start_date else "Campaign start date not set"
                            ], className="text-muted text-center small mb-0")
                        ]) if campaign_start_date else html.Div()
                    ])
                ])
            ], className="mb-3")
        ])
    )

    # Add race visualization if we have all participants data
    if all_participants_data:
        race_fig = create_questionnaire_race_figure(all_participants_data, ranking_data["participant_id"])
        components.append(
            dbc.Card([
                dbc.CardHeader(html.H5("Group Comparison", className="card-title mb-0")),
                dbc.CardBody([
                    dcc.Graph(
                        figure=race_fig,
                        config={'displayModeBar': False, 'responsive': True},
                        style={'width': '100%', 'height': '100%'}
                    )
                ])
            ], className="mb-3", style={"minHeight": "300px"}),
        )
    
    return html.Div(components)
