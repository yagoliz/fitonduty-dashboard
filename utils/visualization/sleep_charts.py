import pandas as pd
import plotly.graph_objects as go

from utils.visualization import create_empty_chart

def create_sleep_trend_chart(df):
    """Create sleep trend chart"""
    if df.empty:
        return create_empty_chart("No sleep data available")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["sleep_hours"],
        marker_color="#4CAF50",
        textposition="outside",
    ))

    # Rectangle for recommended range
    fig.add_shape(
        type="rect",
        xref="paper", yref="y",  # x uses paper coords (0-1), y uses data coords
        x0=0, x1=1,  # Full width of plot area
        y0=7, y1=9,  # Data coordinates for y
        fillcolor="rgba(0,200,0,0.1)",
        line=dict(width=0),
        layer="below",
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(title_text="", tickformat="%b %d", tickangle=-45, automargin=True)
    fig.update_yaxes(title_text="Hours", range=[0, max(10, df["sleep_hours"].max() * 1.1)])
    
    return fig