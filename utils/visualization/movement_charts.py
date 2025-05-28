import plotly.graph_objects as go

from .empty import create_empty_chart

def create_movement_speed_chart(df):
    """Create a bar chart showing movement speed distribution"""
    # Extract movement columns
    movement_cols = ['walking_minutes', 'walking_fast_minutes', 'jogging_minutes', 'running_minutes']
    
    # Check if we have movement data
    if not all(col in df.columns for col in movement_cols):
        return create_empty_chart("No movement speed data available")
    
    # Get movement data (use first row if single day, or average if multiple)
    if len(df) == 1:
        movement_data = df[movement_cols].iloc[0]
    else:
        movement_data = df[movement_cols].mean()
    
    # Create labels and colors
    movement_labels = ['Walking', 'Walking Fast', 'Jogging', 'Running']
    movement_colors = ["#90EE90", "#32CD32", "#FF8C00", "#FF4500"]
    
    # Create chart
    fig = go.Figure()
    
    # Add bars
    for i, (label, minutes) in enumerate(zip(movement_labels, movement_data)):
        fig.add_trace(go.Bar(
            x=[label],
            y=[minutes],
            name=label,
            marker_color=movement_colors[i],
            text=[f"{int(minutes)} min"],
            textposition='auto',
            hovertemplate=f'<b>{label}</b><br>%{{y:.0f}} minutes<extra></extra>',
            showlegend=False
        ))
    
    # Calculate total active minutes
    total_active = sum(movement_data)
    
    fig.update_layout(
        title=f"Movement Speed Distribution<br><sub>Total Active: {int(total_active)} minutes</sub>",
        xaxis_title="Movement Speed",
        yaxis_title="Minutes",
        autosize=True,
        margin=dict(l=20, r=20, t=60, b=20),
        height=None,
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, max(60, max(movement_data) * 1.1)])
    )
    
    return fig