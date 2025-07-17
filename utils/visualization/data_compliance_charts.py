import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ..logging_config import get_logger

logger = get_logger(__name__)


def create_group_data_summary_chart(group_data):
    """Create visualization for group data summary showing data amounts for Past 7 Days and Past 30 Days"""
    
    if not group_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No group data available",
            template='plotly_white',
            height=400
        )
        return fig
    
    # Extract data for plotting
    group_names = [group['group_name'] for group in group_data]
    physio_7_day = [group['physio_7_day_count'] for group in group_data]
    physio_30_day = [group['physio_30_day_count'] for group in group_data]
    quest_7_day = [group['questionnaire_7_day_count'] for group in group_data]
    quest_30_day = [group['questionnaire_30_day_count'] for group in group_data]
    
    # Create subplots - 2 side by side
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Past 7 Days', 'Past 30 Days'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Left plot - Past 7 Days
    fig.add_trace(
        go.Bar(
            x=group_names,
            y=physio_7_day,
            name='Physiological Data',
            marker_color='#1f77b4',
            width=0.4,
            offsetgroup=1
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=group_names,
            y=quest_7_day,
            name='Questionnaire Data',
            marker_color='#ff7f0e',
            width=0.4,
            offsetgroup=2
        ),
        row=1, col=1
    )
    
    # Right plot - Past 30 Days
    fig.add_trace(
        go.Bar(
            x=group_names,
            y=physio_30_day,
            name='Physiological Data',
            marker_color='#1f77b4',
            width=0.4,
            offsetgroup=1,
            showlegend=False  # Don't show legend for duplicate
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=group_names,
            y=quest_30_day,
            name='Questionnaire Data',
            marker_color='#ff7f0e',
            width=0.4,
            offsetgroup=2,
            showlegend=False  # Don't show legend for duplicate
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Group Data Summary - Amount of Data Available",
        title_x=0.5,
        height=500,
        barmode='group',
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Number of Participants with Data", row=1, col=1)
    fig.update_yaxes(title_text="Number of Participants with Data", row=1, col=2)
    
    # Update x-axis labels
    fig.update_xaxes(title_text="Groups", row=1, col=1)
    fig.update_xaxes(title_text="Groups", row=1, col=2)
    
    return fig


def create_group_daily_line_chart(daily_data):
    """Create line plots showing daily data counts for physiological and questionnaire data"""
    from plotly.subplots import make_subplots
    import pandas as pd
    
    if not daily_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No daily data available",
            template='plotly_white',
            height=400
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(daily_data)
    
    # Create subplots - 2 side by side
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Physiological Data', 'Questionnaire Data'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Get unique groups for consistent colors
    groups = df['group_name'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Left plot - Physiological Data
    for i, group in enumerate(groups):
        group_data = df[df['group_name'] == group]
        fig.add_trace(
            go.Scatter(
                x=group_data['date'],
                y=group_data['physio_count'],
                mode='lines+markers',
                name=group,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
    
    # Right plot - Questionnaire Data
    for i, group in enumerate(groups):
        group_data = df[df['group_name'] == group]
        fig.add_trace(
            go.Scatter(
                x=group_data['date'],
                y=group_data['questionnaire_count'],
                mode='lines+markers',
                name=group,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6),
                showlegend=False  # Don't show legend for duplicate
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title_text="Daily Data Availability Trends",
        title_x=0.5,
        height=500,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Number of Participants", row=1, col=1)
    fig.update_yaxes(title_text="Number of Participants", row=1, col=2)
    
    # Update x-axis labels
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    
    # Format x-axis dates
    fig.update_xaxes(tickformat="%b %d", tickangle=-45, row=1, col=1)
    fig.update_xaxes(tickformat="%b %d", tickangle=-45, row=1, col=2)
    
    return fig


def create_group_physiological_line_chart(daily_data):
    """Create line plot showing daily physiological data counts"""
    import pandas as pd
    
    if not daily_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No daily data available",
            template='plotly_white',
            height=400
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(daily_data)
    
    # Create single plot
    fig = go.Figure()
    
    # Get unique groups for consistent colors
    groups = df['group_name'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Add physiological data traces
    for i, group in enumerate(groups):
        group_data = df[df['group_name'] == group]
        fig.add_trace(
            go.Scatter(
                x=group_data['date'],
                y=group_data['physio_count'],
                mode='lines+markers',
                name=group,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            )
        )
    
    # Update layout
    fig.update_layout(
        title_text="Daily Physiological Data Availability",
        title_x=0.5,
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis_title="Date",
        yaxis_title="Number of Participants"
    )
    
    # Format x-axis dates
    fig.update_xaxes(tickformat="%b %d", tickangle=-45)
    
    return fig


def create_group_questionnaire_line_chart(daily_data):
    """Create line plot showing daily questionnaire data counts"""
    import pandas as pd
    
    if not daily_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No daily data available",
            template='plotly_white',
            height=400
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(daily_data)
    
    # Create single plot
    fig = go.Figure()
    
    # Get unique groups for consistent colors
    groups = df['group_name'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Add questionnaire data traces
    for i, group in enumerate(groups):
        group_data = df[df['group_name'] == group]
        fig.add_trace(
            go.Scatter(
                x=group_data['date'],
                y=group_data['questionnaire_count'],
                mode='lines+markers',
                name=group,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            )
        )
    
    # Update layout
    fig.update_layout(
        title_text="Daily Questionnaire Data Availability",
        title_x=0.5,
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis_title="Date",
        yaxis_title="Number of Participants"
    )
    
    # Format x-axis dates
    fig.update_xaxes(tickformat="%b %d", tickangle=-45)
    
    return fig