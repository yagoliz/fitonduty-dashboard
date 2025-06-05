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