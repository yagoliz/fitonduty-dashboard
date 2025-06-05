import plotly.graph_objects as go

from .empty import create_empty_chart


def create_heart_rate_trend_chart(df):
    """Create heart rate trend chart"""
    if df.empty:
        return create_empty_chart("No heart rate data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["resting_hr"],
        mode="lines+markers",
        name="Resting HR",
        line=dict(color="#1976D2", width=2),
        line_shape='spline',
        marker=dict(size=6),
    ))
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["max_hr"],
        mode="lines+markers",
        name="Max HR",
        line=dict(color="#D32F2F", width=2, dash="dot"),
        line_shape='spline',
        marker=dict(size=6),
    ))
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45)
    fig.update_yaxes(title_text="BPM")
    
    return fig


def create_hrv_trend_chart(df):
    """Create HRV trend chart"""
    if df.empty:
        return create_empty_chart("No HRV data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["hrv_rest"],
        mode="lines+markers",
        line=dict(color="#673AB7", width=2),
        line_shape='spline',
        marker=dict(size=6),
    ))
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45)
    fig.update_yaxes(title_text="HRV (ms)")
    
    return fig


def create_heart_rate_zones_chart(df, chart_type='doughnut'):
    """Create a chart showing heart rate zone distribution - can be doughnut or bar"""
    # Extract zone columns (updated for 5 zones)
    zone_cols = ['very_light_percent', 'light_percent', 'moderate_percent', 'intense_percent', 'beast_mode_percent']
    
    # Check if we have zone data
    if not all(col in df.columns for col in zone_cols):
        return create_empty_chart("No heart rate zone data available")
    
    # Get zone percentages (use first row if multiple days, or average if multiple)
    if len(df) == 1:
        zone_data = df[zone_cols].iloc[0]
    else:
        zone_data = df[zone_cols].mean()
    
    # Create zone labels and descriptions
    zone_labels = ['Very Light', 'Light', 'Moderate', 'Intense', 'Beast Mode']
    zone_desc = {
        'Very Light': 'Recovery & Warm-up (50-60% Max HR)',
        'Light': 'Fat Burning (60-70% Max HR)', 
        'Moderate': 'Aerobic Base (70-80% Max HR)',
        'Intense': 'Threshold (80-90% Max HR)',
        'Beast Mode': 'Maximum Effort (90%+ Max HR)'
    }
    
    # Create color gradient from light to intense
    colors = ["#E8F5E8", "#90EE90", "#FFD700", "#FF8C00", "#FF4500"]
    
    # Create chart
    fig = go.Figure()
    
    if chart_type == 'doughnut':
        # Create doughnut chart
        fig.add_trace(go.Pie(
            labels=zone_labels,
            values=zone_data,
            hole=0.4,
            marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>%{percent}<br>%{text}<extra></extra>',
            text=[zone_desc[label] for label in zone_labels]
        ))
        
        # Add center text
        fig.add_annotation(
            text="HR Zones<br><span style='font-size:12px'>Distribution</span>",
            showarrow=False,
            font=dict(size=16, color="#333")
        )
        
        fig.update_layout(
            title="Heart Rate Zone Distribution",
            showlegend=False,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
    else:
        # Create bar chart (fallback)
        for i, (label, value) in enumerate(zip(zone_labels, zone_data)):
            fig.add_trace(go.Bar(
                x=[label],
                y=[value],
                name=label,
                marker_color=colors[i],
                text=[f"{value:.1f}%"],
                textposition='auto',
                hovertext=[f"{label}: {value:.1f}%<br>{zone_desc[label]}"],
                hoverinfo="text",
                showlegend=False
            ))
        
        fig.update_layout(
            title="Heart Rate Zone Distribution",
            xaxis_title="Heart Rate Zones",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, max(100, max(zone_data) * 1.1)])
        )
    
    # Common layout updates
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=20),
        height=None,
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig