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
        autosize=True,
        height=None,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    fig.update_layout(
        # These ensure proper rendering inside the container
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
            text=grouped_df[y_col].round(1),
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

def create_heart_rate_zones_chart(df):
    """Create a bar chart showing heart rate zone distribution"""
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
    
    # Create color gradient from soft red to intense red
    colors = ["#FFB3B3", "#FF9999", "#FF8080", "#FF6666", "#FF4D4D", "#FF3333", "#FF0000"]
    
    # Create chart
    fig = go.Figure()
    
    # Add bar chart
    for i, (label, value) in enumerate(zip(zone_labels, zone_data)):
        fig.add_trace(go.Bar(
            x=[label],
            y=[value],
            name=label,
            marker_color=colors[i],
            text=[f"{value:.1f}%"],
            textposition='auto',
            hovertext=[f"{label}: {value:.1f}%<br>{zone_desc[label]}"],
            hoverinfo="text"
        ))
    
    # Update layout
    fig.update_layout(
        title="Heart Rate Zone Distribution",
        xaxis_title="Heart Rate Zones",
        yaxis_title="Percentage (%)",
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=None,
        template="plotly_white",
        showlegend=False,
        xaxis=dict(
            categoryorder='array',
            categoryarray=zone_labels
        ),
        yaxis=dict(
            range=[0, max(100, max(zone_data) * 1.1)]
        )
    )
    
    return fig


def create_anomaly_timeline(df):
    """Create a timeline chart for daily anomaly scores"""
    if df.empty:
        return create_empty_chart("No anomaly data available for the selected date")
    
    # Calculate anomaly threshold for highlighting
    anomaly_threshold = 0.8
    
    fig = go.Figure()
    
    # Add anomaly score line
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['score'],
        mode='lines+markers',
        line=dict(color="#E91E63", width=2),
        marker=dict(
            size=6,
            color=df['score'],
            colorscale='Viridis',
            cmin=0,
            cmax=max(1, df['score'].max()),
        ),
        hovertemplate='<b>Time:</b> %{x}<br><b>Anomaly Score:</b> %{y:.3f}<extra></extra>'
    ))
    
    # Add threshold line for anomalies
    fig.add_shape(
        type="line",
        x0=min(df['time']),
        x1=max(df['time']),
        y0=anomaly_threshold,
        y1=anomaly_threshold,
        line=dict(color="red", width=1, dash="dash"),
    )
    
    # Add annotation for threshold
    fig.add_annotation(
        x=df['time'].iloc[-1],
        y=anomaly_threshold,
        text="Anomaly Threshold",
        showarrow=False,
        yshift=10,
        font=dict(size=10, color="red")
    )
    
    # Update layout
    fig.update_layout(
        title="Anomaly Score Timeline",
        xaxis=dict(
            title="Time of Day",
            tickangle=-45,
            tickmode='array',
            tickvals=[df['time'].iloc[i] for i in range(0, len(df), max(1, len(df)//12))],  # Show ~12 ticks
        ),
        yaxis=dict(title="Anomaly Score", range=[0, max(1, df['score'].max() * 1.1)]),
        margin=dict(l=10, r=10, t=50, b=50),
        height=None,
        template="plotly_white",
        hovermode="x unified"
    )
    
    return fig

def create_anomaly_heatmap(df_week):
    """Create a heatmap of anomaly scores across multiple days"""
    if df_week.empty:
        return create_empty_chart("No anomaly data available for the selected date range")
    
    # Ensure the dataframe has required columns
    if not all(col in df_week.columns for col in ['date', 'time_slot', 'score']):
        return create_empty_chart("Invalid data format for anomaly heatmap")
    
    # For a meaningful heatmap, we need data for at least 2 days
    if df_week['date'].nunique() < 2:
        return create_empty_chart("Select a date range of at least 2 days for the heatmap view")
    
    # Group data into hourly slots for better visualization
    df_week['hour'] = df_week['time_slot'] // 60
    df_grouped = df_week.groupby(['date', 'hour'])['score'].mean().reset_index()
    
    # Create pivot table
    pivot_df = df_grouped.pivot_table(
        values='score', 
        index='date', 
        columns='hour',
        fill_value=0
    )
    
    # Generate hour labels for x-axis
    x_labels = [f"{h:02d}:00" for h in pivot_df.columns]
    
    # If pivot is empty, return empty chart
    if pivot_df.empty or len(pivot_df.columns) == 0:
        return create_empty_chart("Unable to create heatmap from the available data")
    
    # Determine y-axis ticks based on number of days
    num_days = len(pivot_df.index)
    
    # Intelligently select which dates to show on y-axis
    all_dates = list(pivot_df.index)
    if num_days <= 7:
        # Show all dates if 7 or fewer
        y_tickvals = all_dates
        y_ticktext = [d.strftime('%b %d') for d in all_dates]
    elif num_days <= 14:
        # Show every other date if 8-14 days
        y_tickvals = all_dates[::2]
        y_ticktext = [d.strftime('%b %d') for d in all_dates[::2]]
    elif num_days <= 31:
        # For monthly view, show every week or so
        step = max(2, num_days // 7)  # Show ~7 dates
        y_tickvals = all_dates[::step]
        y_ticktext = [d.strftime('%b %d') for d in all_dates[::step]]
        
        # Always include first and last date
        if all_dates[0] not in y_tickvals:
            y_tickvals = [all_dates[0]] + y_tickvals
            y_ticktext = [all_dates[0].strftime('%b %d')] + y_ticktext
        if all_dates[-1] not in y_tickvals:
            y_tickvals.append(all_dates[-1])
            y_ticktext.append(all_dates[-1].strftime('%b %d'))
    else:
        # For very long ranges, show ~10 evenly spaced dates
        step = max(2, num_days // 10)
        y_tickvals = all_dates[::step]
        y_ticktext = [d.strftime('%b %d') for d in all_dates[::step]]
        
        # Always include first and last date
        if all_dates[0] not in y_tickvals:
            y_tickvals = [all_dates[0]] + y_tickvals
            y_ticktext = [all_dates[0].strftime('%b %d')] + y_ticktext
        if all_dates[-1] not in y_tickvals:
            y_tickvals.append(all_dates[-1])
            y_ticktext.append(all_dates[-1].strftime('%b %d'))
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=x_labels,
        y=all_dates,  # Use all dates for the actual heatmap
        colorscale='Viridis',
        colorbar=dict(
            title="Anomaly Score",
        ),
        zmin=0,
        zmax=0.8,
        hovertemplate='<b>Date:</b> %{y|%b %d, %Y}<br><b>Time:</b> %{x}<br><b>Anomaly Score:</b> %{z:.3f}<extra></extra>'
    ))
    
    # Update layout with custom tick values
    fig.update_layout(
        title={
            'text': "Anomaly Pattern by Day and Time",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title="Time of Day",
            tickangle=-45,
            # Show fewer ticks for readability
            nticks=8,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Date",
            # Use our custom tick values and labels
            tickmode='array',
            tickvals=y_tickvals,
            ticktext=y_ticktext,
            tickfont=dict(size=10)
        ),
        margin=dict(l=5, r=5, t=40, b=40),
        autosize=True,
        height=None,
        template="plotly_white"
    )
    
    return fig