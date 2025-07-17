import plotly.graph_objects as go

from .empty import create_empty_chart

def create_data_count_chart(df, y_col, title, color='#007bff'):
    """Create a line chart showing data collection counts over time"""
    if df.empty:
        return create_empty_chart(title)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[y_col],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=2),
        line_shape='spline',
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Number of Participants",
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20),
        template='plotly_white',
        autosize=True,
        height=None,
    )
    
    return fig


def create_dual_axis_physiological_chart(df):
    """Create a chart showing physiological metrics with dual y-axes"""
    if df.empty:
        return create_empty_chart("Average Physiological Metrics")
    
    # Filter out rows where both physiological metrics are null
    df_clean = df.dropna(subset=['avg_resting_hr', 'avg_sleep_hours'], how='all')
    
    if df_clean.empty:
        return create_empty_chart("Average Physiological Metrics")
    
    fig = go.Figure()
    
    # Add resting heart rate (only for non-null values)
    df_hr = df_clean.dropna(subset=['avg_resting_hr'])
    if not df_hr.empty:
        fig.add_trace(go.Scatter(
            x=df_hr['date'],
            y=df_hr['avg_resting_hr'],
            mode='lines+markers',
            name='Avg Resting HR (bpm)',
            line=dict(color='#dc3545', width=2),
            line_shape='spline',
            marker=dict(size=4),
            yaxis='y1'
        ))
    
    # Add sleep hours (only for non-null values)
    df_sleep = df_clean.dropna(subset=['avg_sleep_hours'])
    if not df_sleep.empty:
        fig.add_trace(go.Scatter(
            x=df_sleep['date'],
            y=df_sleep['avg_sleep_hours'],
            mode='lines+markers',
            name='Avg Sleep Hours',
            line=dict(color='#6f42c1', width=2),
            line_shape='spline',
            marker=dict(size=4),
            yaxis='y2'
        ))
    
    fig.update_layout(
        title="Average Physiological Metrics",
        xaxis_title="Date",
        yaxis=dict(
            title="Resting HR (bpm)",
            side="left",
            color='#dc3545',
            range=[40, 100],
        ),
        yaxis2=dict(
            title="Sleep Hours",
            side="right",
            overlaying="y",
            color='#6f42c1',
            range=[0, 10],
        ),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20),
        template='plotly_white',
        autosize=True,
        height=None,
    )

    # Put legend on the top and one row
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.95,
        xanchor="center",
        x=0.5,
        bgcolor='rgba(0,0,0,0)' 
    ))
    
    return fig


def create_subjective_metrics_chart(df):
    """Create a chart showing subjective assessment metrics"""
    if df.empty:
        return create_empty_chart("Average Subjective Assessment Metrics")
    
    # Filter out rows where all subjective metrics are null
    df_clean = df.dropna(subset=['avg_sleep_quality', 'avg_fatigue_level', 'avg_motivation_level'], how='all')
    
    if df_clean.empty:
        return create_empty_chart("Average Subjective Assessment Metrics")
    
    fig = go.Figure()
    
    # Add sleep quality (only for non-null values)
    df_sleep_quality = df_clean.dropna(subset=['avg_sleep_quality'])
    if not df_sleep_quality.empty:
        fig.add_trace(go.Scatter(
            x=df_sleep_quality['date'],
            y=df_sleep_quality['avg_sleep_quality'],
            mode='lines+markers',
            name='Avg Sleep Quality',
            line=dict(color='#20c997', width=2),
            line_shape='spline',
            marker=dict(size=4)
        ))
    
    # Add fatigue level (only for non-null values)
    df_fatigue = df_clean.dropna(subset=['avg_fatigue_level'])
    if not df_fatigue.empty:
        fig.add_trace(go.Scatter(
            x=df_fatigue['date'],
            y=df_fatigue['avg_fatigue_level'],
            mode='lines+markers',
            name='Avg Fatigue Level',
            line=dict(color='#fd7e14', width=2),
            line_shape='spline',
            marker=dict(size=4)
        ))
    
    # Add motivation level (only for non-null values)
    df_motivation = df_clean.dropna(subset=['avg_motivation_level'])
    if not df_motivation.empty:
        fig.add_trace(go.Scatter(
            x=df_motivation['date'],
            y=df_motivation['avg_motivation_level'],
            mode='lines+markers',
            name='Avg Motivation Level',
            line=dict(color='#198754', width=2),
            line_shape='spline',
            marker=dict(size=4)
        ))
    
    fig.update_layout(
        title="Average Subjective Assessment Metrics",
        xaxis_title="Date",
        yaxis_title="Score (0-100)",
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20),
        template='plotly_white',
        autosize=True,
        height=None,
        yaxis=dict(
            range=[0, 105],
            tickmode='linear',
            dtick=20
        )
    )

    # Put legend on the top and one row
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.95,
        xanchor="center",
        x=0.5,
        bgcolor='rgba(0,0,0,0)' 
    ))
    
    return fig
