from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from components.participant.ranking_over_time import create_ranking_over_time_figure

def create_race_figure(participant_data, current_participant_id):
    """
    Create a race-style visualization showing participant's position among peers
    
    Args:
        participant_data: List of dictionaries with participant data
        current_participant_id: ID of the current participant
        
    Returns:
        Plotly figure object
    """
    # Extract data volumes (days with data) for all participants
    volumes = []
    participant_volume = 0
    participant_username = ""
    
    for p in participant_data:
        if p['participant_id'] == current_participant_id:
            participant_volume = p['days_with_data']
            participant_username = p.get('username', 'You')
        else:
            volumes.append({
                'volume': p['days_with_data'],
                'username': p.get('username', f"Participant {p['participant_id']}")
            })
    
    # Sort other participants by volume
    volumes.sort(key=lambda x: x['volume'], reverse=True)
    
    # Extract just the volumes for normalization
    vol_values = [v['volume'] for v in volumes]
    
    # Convert to numpy arrays
    vol = np.array(vol_values) if vol_values else np.array([])
    part = participant_volume
    
    # Calculate max value for normalization
    all_volumes = list(vol) + [part]
    max_vol = max(all_volumes) if all_volumes else 1
    
    # Normalize data values
    vol_normalized = np.round(vol/max_vol, 8) if len(vol) > 0 else np.array([])
    part_normalized = np.round(part/max_vol, 8)
    
    # Choose emoji based on the participant's relative position
    emojis = ['🥺', '😐', '😊', '😎', '👑']
    
    if part_normalized < 0.25:
        emoji = emojis[0] 
    elif part_normalized < 0.5:
        emoji = emojis[1]
    elif part_normalized < 0.8:
        emoji = emojis[2]
    elif part_normalized < 1:
        emoji = emojis[3]
    else:
        emoji = emojis[4]
    
    # Create arrays for the y axis (spreading participants vertically)
    n_others = len(vol_normalized)
    if n_others > 0:
        # Spread participants evenly but with some randomness
        base_positions = np.linspace(-0.4, 0.4, n_others)
        # Add small random offset for more natural look
        y_positions = base_positions + np.random.uniform(-0.05, 0.05, n_others)
    else:
        y_positions = np.array([])
    
    # Create the figure
    fig = go.Figure()
    
    # Add track lanes
    for i in range(-2, 3):
        y_pos = i * 0.2
        fig.add_shape(
            type="line",
            x0=-0.05, x1=1.1,
            y0=y_pos, y1=y_pos,
            line=dict(
                color="rgba(150, 150, 150, 0.3)",
                width=1,
                dash="dash"
            ),
            layer="below"
        )
    
    # Add trace for other participants
    if len(vol_normalized) > 0:
        # Create hover text
        hover_texts = [f"{v['username']}<br>{v['volume']} days ({vol_normalized[i]:.1%})" 
                      for i, v in enumerate(volumes)]
        
        fig.add_trace(go.Scatter(
            x=vol_normalized, 
            y=y_positions, 
            mode='markers', 
            name='Other participants',
            marker=dict(
                size=30, 
                color=vol_normalized,
                colorscale='Gray',
                cmin=0,
                cmax=1,
                opacity=0.7,
                line=dict(
                    width=2,
                    color='darkblue'
                ),
                symbol='circle'
            ),
            # text=hover_texts,
            # hovertemplate='%{text}<extra></extra>',
            showlegend=False
        ))
    
    # Add trace for current participant with glow effect
    fig.add_trace(go.Scatter(
        x=[part_normalized], 
        y=[0], 
        mode='text+markers',
        name='You',
        text=[emoji],
        textposition="middle center",
        textfont=dict(size=45),
        marker=dict(
            size=40,
            color='gold',
            opacity=0.3,
            line=dict(width=0)
        ),
        hovertemplate=f'{participant_username}<br>{participant_volume} days ({part_normalized:.1%})<br><b>Your position</b><extra></extra>',
        showlegend=False
    ))
    
    # Add finish line
    fig.add_shape(
        type="line",
        x0=1, x1=1,
        y0=-0.6, y1=0.6,
        line=dict(
            color="green",
            width=4,
            dash="dash",
        )
    )
    
    # Add start line
    fig.add_shape(
        type="line",
        x0=0, x1=0,
        y0=-0.6, y1=0.6,
        line=dict(
            color="gray",
            width=2,
        )
    )
    
    # Add labels
    fig.add_annotation(
        x=1,
        y=0.7,
        text="🏁 100% Complete",
        showarrow=False,
        font=dict(size=14, color="green", weight=600)
    )
    
    fig.add_annotation(
        x=0,
        y=0.7,
        text="Start",
        showarrow=False,
        font=dict(size=12, color="gray")
    )
    
    # Add position indicator
    rank = sum(1 for v in vol_values if v > part) + 1
    total = len(vol_values) + 1
    
    fig.add_annotation(
        x=part_normalized,
        y=-0.7,
        text=f"Position: {rank}/{total}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="rgba(0, 0, 0, 0.4)",
        ax=0,
        ay=-30,
        font=dict(size=12, weight=600)
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="🏃 Your Position in the Data Consistency Race",
            font=dict(size=18, weight=600),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Progress to Goal →",
            showticklabels=True,
            showgrid=True,
            zeroline=False,
            range=[-0.1, 1.15],
            tickformat='.0%',
            gridcolor='rgba(0,0,0,0.05)',
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=['0%', '25%', '50%', '75%', '100%']
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-0.8, 0.8]
        ),
        showlegend=False,
        height=280,
        margin=dict(l=20, r=20, t=50, b=60),
        plot_bgcolor='rgba(248, 249, 250, 0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    # Add gradient background for the track
    fig.add_shape(
        type="rect",
        x0=-0.1, x1=1.15,
        y0=-0.6, y1=0.6,
        fillcolor="rgba(200, 200, 200, 0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    return fig


def create_participant_ranking_layout(ranking_data, all_participants_data=None):
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