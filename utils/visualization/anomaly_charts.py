import plotly.graph_objects as go

from .empty import create_empty_chart

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