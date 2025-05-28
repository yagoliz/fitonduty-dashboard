from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


def create_participant_ranking_layout(ranking_data):
    """
    Create a component showing the participant's ranking within their group
    
    Args:
        ranking_data: Dictionary with ranking information
        
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
        rank_text = "You're in first place!"
    elif ranking_data["rank"] <= 3:
        rank_color = "info"
        rank_text = "You're in the top 3!"
    elif ranking_data["rank"] <= ranking_data["total_participants"] / 2:
        rank_color = "primary"
        rank_text = "You're in the top half!"
    else:
        rank_color = "warning"
        rank_text = "Keep going!"
    
    return dbc.Card([
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
                        # html.Strong(f"{ranking_data['days_with_data']} of {ranking_data['total_possible_days']} days"),
                        html.Strong(f"{ranking_data['days_with_data']} days!"),
                        # f" ({ranking_data['consistency_percentage']:.1f}%)"
                    ], className="text-center mb-0")
                ])
            ])
        ])
    ], className="border-0 bg-light mb-3")