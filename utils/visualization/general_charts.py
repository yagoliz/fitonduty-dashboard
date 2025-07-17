import plotly.graph_objects as go

def create_group_bar_chart(df, x_col, y_col, title, y_label, color):
    """Create a bar chart for group comparison"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Group',
        yaxis_title=y_label,
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template='plotly_white'
    )
    
    return fig

def create_participant_bar_chart(df, x_col, y_cols, names, colors, title, y_label):
    """Create a bar chart comparing participants for one or more metrics"""
    fig = go.Figure()
    
    grouped_df = df.groupby(x_col)[y_cols].mean().reset_index()
    
    # Add a trace for each metric
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=grouped_df[x_col],
            y=grouped_df[y_col],
            name=names[i],
            marker_color=colors[i],
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Participant',
        yaxis_title=y_label,
        barmode='group',
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_history_line_chart(df, y_cols, names, colors, title, y_label, add_range=False, range_min=None, range_max=None):
    """Create a line chart showing historical data"""
    fig = go.Figure()
    
    # Add a trace for each metric
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[y_col],
            mode='lines+markers',
            name=names[i],
            line=dict(color=colors[i], width=2),
            marker=dict(size=6)
        ))
    
    # Add recommended range if specified
    if add_range and range_min is not None and range_max is not None:
        fig.add_shape(
            type="rect",
            x0=df['date'].min(),
            x1=df['date'].max(),
            y0=range_min,
            y1=range_max,
            fillcolor="rgba(0,200,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        fig.add_annotation(
            x=df['date'].max(),
            y=(range_min + range_max) / 2,
            text="Recommended Range",
            showarrow=False,
            font=dict(size=10, color="green")
        )
    
    # Format x-axis dates
    fig.update_xaxes(
        tickformat="%b %d",
        tickangle=-45
    )

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=y_label,
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_dual_axis_chart(df, x_col, y1_col, y2_col, y1_name, y2_name, y1_color, y2_color, title):
    """Create a chart with dual y-axes"""
    fig = go.Figure()
    
    # Add bars for first metric
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y1_col],
        name=y1_name,
        marker_color=y1_color,
        yaxis='y'
    ))
    
    # Add line for second metric
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        name=y2_name,
        mode='lines+markers',
        line=dict(color=y2_color, width=2),
        marker=dict(size=6),
        yaxis='y2'
    ))
    
    # Update layout for dual axis
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Date",
            tickformat="%b %d",
            tickangle=-45
        ),
        yaxis=dict(
            title=y1_name,
            titlefont=dict(color=y1_color),
            tickfont=dict(color=y1_color)
        ),
        yaxis2=dict(
            title=y2_name,
            titlefont=dict(color=y2_color),
            tickfont=dict(color=y2_color),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        autosize=True,
        height=None,
        margin=dict(l=60, r=60, t=60, b=60),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_group_data_summary_chart(group_data):
    """Create visualization for group data summary showing data amounts for Past 7 Days and Past 30 Days"""
    from plotly.subplots import make_subplots
    
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