from dash import html
import dash_bootstrap_components as dbc
from plotly import graph_objects as go

from .empty import create_empty_chart

def create_step_count_summary(df):
    """Create step count summary statistics"""
    if df.empty:
        return html.Div("No data available")
    
    avg_steps = df["step_count"].mean()
    min_steps = df["step_count"].min()
    max_steps = df["step_count"].max()
    
    # Calculate days meeting goal
    goal_days = (df["step_count"] >= 10000).sum()
    total_days = len(df)
    goal_percentage = (goal_days / total_days * 100) if total_days > 0 else 0
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3(f"{avg_steps:,.0f}", className="text-primary text-center"),
                html.P("Avg Steps", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3(f"{max_steps:,}", className="text-success text-center"),
                html.P("Best Day", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3(f"{min_steps:,}", className="text-danger text-center"),
                html.P("Least Active", className="text-muted text-center small"),
            ], width=3),
            dbc.Col([
                html.H3(f"{goal_percentage:.0f}%", className="text-warning text-center"),
                html.P("Goal Days", className="text-muted text-center small"),
            ], width=3),
        ])
    ])


def create_step_count_trend_chart(df):
    """Create step count trend chart"""
    if df.empty:
        return create_empty_chart("No step count data available")
    
    fig = go.Figure()
    
    # Add step count bars
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["step_count"],
        marker_color=df["step_count"].apply(lambda x: "#4CAF50" if x >= 10000 else "#FFA726"),
        textposition="outside",
        hovertemplate='<b>Date:</b> %{x}<br><b>Steps:</b> %{y}<extra></extra>',
    ))
    
    # Add goal line at 10,000 steps
    fig.add_shape(
        type="line",
        xref="paper",
        x0=0,
        x1=1,
        y0=10000,
        y1=10000,
        line=dict(color="red", width=2, dash="dash"),
    )
    
    fig.add_annotation(
        x=df["date"].max(),
        y=10000,
        text="Goal: 10,000",
        showarrow=False,
        yshift=10,
        xshift=-20,
        font=dict(size=10, color="red")
    )
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=35),
        height=None,
        template="plotly_white",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            title="Steps",
            range=[0, max(12000, df["step_count"].max() * 1.1)]
        ),
        xaxis=dict(
            title="",
            tickformat="%b %d",
            tickangle=-45
        )
    )
    
    return fig