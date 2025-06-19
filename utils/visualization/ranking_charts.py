import numpy as np
import pandas as pd
import plotly.graph_objects as go


def create_race_figure(participant_data: dict, current_participant_id: int) -> go.Figure:
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
            participant_volume = float(p.get('data_volume_mb', 0))
            participant_username = p.get('username', 'You')
        else:
            volumes.append({
                'data_size': float(p.get('data_volume_mb', 0)),
                'username': p.get('username', f"Participant {p['participant_id']}")
            })
    
    # Sort other participants by volume
    volumes.sort(key=lambda x: x['data_size'], reverse=True)
    
    # Extract just the volumes for normalization
    vol_values = [v['data_size'] for v in volumes]
    
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
                color="white",
                width=1,
                # dash="dash"
            ),
            layer="between"
        )
    
    # Add trace for other participants
    if len(vol_normalized) > 0:
        
        fig.add_trace(go.Scatter(
            x=vol_normalized, 
            y=y_positions, 
            mode='markers', 
            name='Other participants',
            marker=dict(
                size=30, 
                color="rgba(150, 150, 150, 0.5)",
                opacity=0.7,
                line=dict(
                    width=2,
                    color='rgba(50, 50, 50, 0.8)'
                ),
                symbol='circle'
            ),
            # text=hover_texts,
            # hovertemplate='%{text}<extra></extra>',
            hoverinfo="skip",
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
            color="white",
            width=2,
        )
    )
    
    # Add labels
    fig.add_annotation(
        x=1,
        y=0.7,
        text="🏁 Leader",
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
        # title=dict(
        #     text="🏃 Your Position in the Data Consistency Race",
        #     font=dict(size=18, weight=600),
        #     x=0.5,
        #     xanchor='center'
        # ),
        title="Your Data Consistency",
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
        height=None,
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
        fillcolor="rgba(221, 17, 17, 0.4)",
        line=dict(width=0),
        layer="below"
    )
    
    return fig


def create_ranking_over_time_figure(user_id, df_history, interval='week'):
    """
    Create a ranking over time figure based on historical data.
    
    Args:
        user_id: Current user's ID
        df_history: DataFrame with all participants' historical data
        interval: 'week' or 'month' for grouping
        
    Returns:
        Plotly figure object
    """
    if df_history.empty:
        return None
    
    # Group data by interval
    if interval == 'week':
        df_history['period'] = pd.to_datetime(df_history['date']).dt.to_period('W')
        period_label = 'Week'
    else:
        df_history['period'] = pd.to_datetime(df_history['date']).dt.to_period('M')
        period_label = 'Month'
    
    # Calculate data availability for each participant in each period
    period_data = df_history.groupby(['period', 'participant_id']).size().reset_index(name='days_with_data')
    
    # Get unique periods and participants
    periods = sorted(period_data['period'].unique())
    participants = period_data['participant_id'].unique()
    
    # Initialize lists for tracking rankings
    weekly_ranks = []
    cumulative_ranks = []
    period_labels = []
    
    cumulative_data = {p: 0 for p in participants}
    
    for period in periods:
        # Get data for this period
        period_df = period_data[period_data['period'] == period]
        
        # Calculate weekly ranking
        period_values = {row['participant_id']: row['days_with_data'] 
                        for _, row in period_df.iterrows()}
        
        # Fill missing participants with 0
        for p in participants:
            if p not in period_values:
                period_values[p] = 0
        
        # Calculate rank for current user
        user_value = period_values.get(user_id, 0)
        user_rank = sum(1 for v in period_values.values() if v > user_value) + 1
        weekly_ranks.append(user_rank)
        
        # Update cumulative data
        for p, v in period_values.items():
            cumulative_data[p] += v
        
        # Calculate cumulative rank
        user_cumulative = cumulative_data[user_id]
        cumulative_rank = sum(1 for v in cumulative_data.values() if v > user_cumulative) + 1
        cumulative_ranks.append(cumulative_rank)
        
        # Format period label
        if interval == 'week':
            period_labels.append(period.start_time.strftime('%b %d'))
        else:
            period_labels.append(period.start_time.strftime('%b %Y'))
    
    # Create figure
    fig = go.Figure()
    
    # Add weekly ranking trace
    fig.add_trace(go.Scatter(
        x=period_labels,
        y=weekly_ranks,
        mode='lines+markers',
        name=f'{period_label}ly Ranking',
        marker=dict(color='#1976D2', size=10),
        line=dict(color='#1976D2', width=2),
        hovertemplate=f'{period_label}: %{{x}}<br>Rank: %{{y}}<extra></extra>'
    ))
    
    # Add cumulative ranking trace
    fig.add_trace(go.Scatter(
        x=period_labels,
        y=cumulative_ranks,
        mode='lines+markers',
        name='Overall Ranking',
        marker=dict(color='#38b000', size=10),
        line=dict(color='#38b000', width=2),
        hovertemplate='%{x}<br>Overall Rank: %{y}<extra></extra>'
    ))
    
    # Calculate y-axis range
    total_participants = len(participants)
    y_max = total_participants + (5 - (total_participants % 5)) + 1
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='Your Ranking Progress Over Time',
            font=dict(size=16),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=period_label,
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title='Ranking Position',
            range=[y_max, 0],  # Invert axis so rank 1 is at top
            dtick=1,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=300,
        margin=dict(l=20, r=20, t=60, b=60),
        plot_bgcolor='rgba(248, 249, 250, 0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    # Add reference lines for top positions
    for rank in [1, 3]:
        fig.add_shape(
            type="line",
            x0=period_labels[0], x1=period_labels[-1],
            y0=rank, y1=rank,
            line=dict(
                color="rgba(0,0,0,0.2)",
                width=1,
                dash="dot"
            )
        )
    
    # Add annotation for first place
    fig.add_annotation(
        x=period_labels[-1],
        y=1,
        text="1st",
        showarrow=False,
        xshift=20,
        font=dict(size=10, color="rgba(0,0,0,0.5)")
    )
    
    return fig


def create_ranking_trend_summary(ranking_history):
    """
    Create a summary card showing ranking trends
    
    Args:
        ranking_history: List of ranking data over time
        
    Returns:
        Dash component with trend summary
    """
    if not ranking_history or len(ranking_history) < 2:
        return None
    
    # Calculate trend
    first_rank = ranking_history[0]['rank']
    last_rank = ranking_history[-1]['rank']
    rank_change = first_rank - last_rank  # Positive means improvement
    
    # Determine trend direction and color
    if rank_change > 0:
        trend_icon = "📈"
        trend_text = f"Improved by {rank_change} position{'s' if rank_change > 1 else ''}"
        trend_color = "success"
    elif rank_change < 0:
        trend_icon = "📉"
        trend_text = f"Dropped by {abs(rank_change)} position{'s' if abs(rank_change) > 1 else ''}"
        trend_color = "danger"
    else:
        trend_icon = "➡️"
        trend_text = "Maintained position"
        trend_color = "primary"
    
    # Calculate best and worst ranks
    best_rank = min(r['rank'] for r in ranking_history)
    # worst_rank = max(r['rank'] for r in ranking_history)
    
    from dash import html
    import dash_bootstrap_components as dbc
    
    return dbc.Card([
        dbc.CardHeader(html.H6("Ranking Trend", className="mb-0")),
        dbc.CardBody([
            html.Div([
                html.Span(trend_icon, className="me-2", style={"fontSize": "24px"}),
                html.Span(trend_text, className=f"text-{trend_color}")
            ], className="mb-2"),
            html.Hr(className="my-2"),
            html.Div([
                html.Small([
                    html.Strong("Best: "), f"#{best_rank}",
                    html.Span(" | ", className="mx-1"),
                    html.Strong("Current: "), f"#{last_rank}"
                ], className="text-muted")
            ])
        ])
    ], className="mb-3")