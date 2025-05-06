# utils/visualization.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_empty_chart(message):
    """
    Create an empty chart with a message
    
    Args:
        message: Message to display
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    fig.update_layout(
        title=message,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 16
                }
            }
        ],
        height=300
    )
    
    return fig

def create_group_bar_chart(df, x_col, y_col, title, y_label, color):
    """Create a bar chart for group comparison"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        text=df[y_col].round(1),
        textposition='auto'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Group',
        yaxis_title=y_label,
        margin=dict(l=40, r=40, t=60, b=40),
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
            text=grouped_df[y_col].round(1),
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Participant',
        yaxis_title=y_label,
        barmode='group',
        margin=dict(l=40, r=40, t=60, b=60),
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
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=y_label,
        margin=dict(l=40, r=40, t=60, b=40),
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Format x-axis dates
    fig.update_xaxes(
        tickformat="%b %d",
        tickangle=-45
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
        margin=dict(l=60, r=60, t=60, b=60),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_heart_rate_zones_chart(df):
    """Create a pie chart showing heart rate zone distribution"""
    # Extract zone columns
    zone_cols = [f'zone{i}_percent' for i in range(1, 8)]
    
    # Check if we have zone data
    if not all(col in df.columns for col in zone_cols):
        # Create empty chart with message
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text="No heart rate zone data available",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=300
        )
        return fig
    
    # Get zone percentages (use first row if multiple days)
    zone_data = df[zone_cols].iloc[0]
    
    # Create zone labels
    zone_labels = [f"Zone {i}" for i in range(1, 8)]
    
    # Create zone descriptions
    zone_desc = {
        'Zone 1': 'Very Light (50-60% Max HR)',
        'Zone 2': 'Light (60-70% Max HR)',
        'Zone 3': 'Moderate (70-80% Max HR)',
        'Zone 4': 'Hard (80-90% Max HR)',
        'Zone 5': 'Very Hard (90-100% Max HR)',
        'Zone 6': 'Anaerobic (100-110% Max HR)',
        'Zone 7': 'Maximal (110%+ Max HR)'
    }
    
    # Create hover text
    hover_text = [f"{label}: {zone_data[i]:.1f}%<br>{zone_desc[label]}" 
                 for i, label in enumerate(zone_labels)]
    
    # Colors for zones
    colors = ["#80d8ff", "#4dd0e1", "#26c6da", "#26a69a", "#9ccc65", "#ffee58", "#ffab91"]
    
    # Create chart
    fig = go.Figure()
    
    # Add pie chart
    fig.add_trace(go.Pie(
        labels=zone_labels,
        values=zone_data,
        text=[zone_desc[label] for label in zone_labels],
        hovertext=hover_text,
        textinfo='label+percent',
        marker=dict(colors=colors),
        hole=0.3
    ))
    
    # Update layout
    fig.update_layout(
        title="Heart Rate Zone Distribution",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig