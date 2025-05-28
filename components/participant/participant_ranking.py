from dash import html, dcc
import dash_bootstrap_components as dbc

from utils.visualization import create_race_figure

def create_participant_ranking(ranking_data, all_participants_data=None):
    """
    Create a component showing the participant's ranking within their group
    
    Args:
        ranking_data: Dictionary with ranking information
        all_participants_data: Optional list of all participants' data for race visualization
        
    Returns:
        A dash component showing the ranking information
    """
    if not ranking_data:
        return html.Div(
            dbc.Alert("Ranking information not available", color="warning"),
            className="mb-3"
        )
    
    # Calculate percentage for progress bar
    rank_percentage = (1 - ((ranking_data["rank"] - 1) / ranking_data["total_participants"])) * 100 if ranking_data["total_participants"] > 1 else 100
    
    # Create color based on rank
    if ranking_data["rank"] == 1:
        rank_color = "success"
        rank_text = "You're in first place! 🏆"
    elif ranking_data["rank"] <= 3:
        rank_color = "info"
        rank_text = "You're in the top 3! 🥉"
    elif ranking_data["rank"] <= ranking_data["total_participants"] / 2:
        rank_color = "primary"
        rank_text = "You're in the top half! 💪"
    else:
        rank_color = "warning"
        rank_text = "It's not too late! Keep going! 🚀"
    
    components = [
        # Ranking Summary Card
        dbc.Card([
            dbc.CardHeader(html.H5("Your Data Consistency Ranking", className="card-title mb-0")),
            dbc.CardBody([
                html.Div([
                    html.H2(
                        f"{ranking_data['rank']}/{ranking_data['total_participants']}",
                        className=f"text-{rank_color} text-center"
                    ),
                    html.P(rank_text, className="text-center mb-2"),
                    
                    dbc.Progress(
                        value=rank_percentage,
                        color=rank_color,
                        className="mb-3",
                        style={"height": "10px"}
                    ),
                    
                    html.Div([
                        html.P([
                            "You've provided data for ",
                            html.Strong(f"{ranking_data['days_with_data']} days!"),
                        ], className="text-center mb-0")
                    ])
                ])
            ])
        ], className="border-0 bg-light mb-3"),
    ]
    
    # Add race visualization if we have all participants data
    if all_participants_data:
        race_fig = create_race_figure(all_participants_data, ranking_data["participant_id"])
        components.append(
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=race_fig,
                        config={'displayModeBar': False, 'responsive': True},
                        style={'width': '100%', 'height': '100%'}
                    )
                ])
            ], className="border-0 bg-light")
        )
    
    return html.Div(components)
