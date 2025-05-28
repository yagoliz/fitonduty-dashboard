# components/participant/ranking_over_time.py
import plotly.graph_objects as go
import pandas as pd


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
    worst_rank = max(r['rank'] for r in ranking_history)
    
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