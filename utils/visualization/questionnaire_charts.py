import pandas as pd
import plotly.graph_objects as go

from .empty import create_empty_chart

def create_sleep_quality_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create sleep quality trend chart from questionnaire data"""
    if df.empty:
        return create_empty_chart("No sleep quality data available")
    
    fig = go.Figure()
    
    # Add sleep quality line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["perceived_sleep_quality"],
        mode="lines+markers",
        name="Sleep Quality",
        line=dict(color="#4CAF50", width=3),
        line_shape='spline',
        marker=dict(size=8, color="#4CAF50"),
        hovertemplate='<b>Date:</b> %{x}<br><b>Sleep Quality:</b> %{y}<extra></extra>',
    ))
    
    # Add reference lines for quality levels
    fig.add_shape(
        type="line",
        xref="paper", yref="y",
        x0=0, x1=1,
        y0=70, y1=70,
        line=dict(color="green", width=1, dash="dash"),
        opacity=0.9
    )
    
    fig.add_shape(
        type="line",
        xref="paper", yref="y",
        x0=0, x1=1,
        y0=40, y1=40,
        line=dict(color="orange", width=1, dash="dash"),
        opacity=0.9
    )
    
    # Add annotations for reference lines
    fig.add_annotation(
        xref="paper", x=0.02,
        y=70, yshift=10,
        text="Good (70+)",
        showarrow=False,
        font=dict(size=10, color="green"),
        opacity=0.7
    )
    
    fig.add_annotation(
        xref="paper", x=0.02,
        y=40, yshift=10,
        text="Fair (40-60)",
        showarrow=False,
        font=dict(size=10, color="orange"),
        opacity=0.7
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            title="Sleep Quality Rating",
            range=[0, 105],
            dtick=20,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        xaxis=dict(
            title="",
            tickformat="%b %d",
            tickangle=-45,
            gridcolor='rgba(0,0,0,0.1)'
        )
    )
    
    return fig


def create_fatigue_motivation_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create combined fatigue and motivation trend chart"""
    if df.empty:
        return create_empty_chart("No fatigue/motivation data available")
    
    fig = go.Figure()
    
    # Add fatigue level (inverted for better interpretation - lower is better)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["fatigue_level"],
        mode="lines+markers",
        name="Fatigue Level",
        line=dict(color="#FF6B6B", width=2),
        line_shape='spline',
        marker=dict(size=6, color="#FF6B6B"),
        hovertemplate='<b>Date:</b> %{x}<br><b>Fatigue:</b> %{y}/100<extra></extra>',
    ))
    
    # Add motivation level
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["motivation_level"],
        mode="lines+markers",
        name="Motivation Level",
        line=dict(color="#2196F3", width=2),
        line_shape='spline',
        marker=dict(size=6, color="#2196F3"),
        hovertemplate='<b>Date:</b> %{x}<br><b>Motivation:</b> %{y}/100<extra></extra>',
    ))
    
    # Add reference zones
    # High motivation zone (70-100)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1,
        y0=70, y1=100,
        fillcolor="rgba(33, 150, 243, 0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    # Low fatigue zone (10-30)
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",
        x0=0, x1=1,
        y0=0, y1=30,
        fillcolor="rgba(76, 175, 80, 0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    # Add annotations
    fig.add_annotation(
        xref="paper", x=0.98,
        y=85, 
        text="High Motivation",
        showarrow=False,
        font=dict(size=10, color="#2196F3"),
        opacity=0.7,
        xanchor="right"
    )
    
    fig.add_annotation(
        xref="paper", x=0.98,
        y=20, 
        text="Low Fatigue",
        showarrow=False,
        font=dict(size=10, color="#4CAF50"),
        opacity=0.7,
        xanchor="right"
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        autosize=True,
        height=None,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            title="Rating (0-100)",
            range=[0, 105],
            dtick=20,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        xaxis=dict(
            title="",
            tickformat="%b %d",
            tickangle=-45,
            gridcolor='rgba(0,0,0,0.1)'
        )
    )
    
    return fig

