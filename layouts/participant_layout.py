# layouts/participant_layout.py
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
from flask_login import current_user
from dash.exceptions import PreventUpdate
import numpy as np

# Import the footer component
from layouts.footer import create_footer
from utils.database import load_participant_data

def create_layout():
    """
    Create the layout for the participant dashboard
    
    Returns:
        A dash component with the participant dashboard
    """
    # Get the current participant's information
    user_id = current_user.id if current_user.is_authenticated else None
    display_name = current_user.display_name if current_user.is_authenticated else "Not logged in"
    
    # Get group information
    group = current_user.group if current_user.is_authenticated else None
    
    # Create last 7 days date range for default view
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    
    return dbc.Container([
        # Navigation bar
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.svg", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("Health Dashboard", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.Button("Logout", id="logout-button", color="danger", outline=True)),
                    ],
                    className="ms-auto",
                    navbar=True),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
        ),
        
        # Header section with user info
        dbc.Row([
            dbc.Col([
                html.H1("Your Health Dashboard", className="display-4"),
                html.P(f"Welcome {display_name}!", className="lead"),
                html.Hr(className="my-4"),
                html.P(f"Group: {group}" if group else "", className="lead"),
            ])
        ], className="mb-4"),
        
        # Date selector
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Select Date Range", className="card-title"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("From:"),
                                dcc.DatePickerSingle(
                                    id="participant-start-date",
                                    date=week_ago,
                                    display_format="YYYY-MM-DD",
                                    className="mb-2"
                                ),
                            ], width=6),
                            dbc.Col([
                                dbc.Label("To:"),
                                dcc.DatePickerSingle(
                                    id="participant-end-date",
                                    date=today,
                                    display_format="YYYY-MM-DD",
                                    className="mb-2"
                                ),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("Last 7 Days", id="btn-last-7-days", color="secondary", size="sm", className="me-1"),
                                dbc.Button("Last 30 Days", id="btn-last-30-days", color="secondary", size="sm", className="me-1"),
                                dbc.Button("This Month", id="btn-this-month", color="secondary", size="sm"),
                            ])
                        ], className="mt-2"),
                    ])
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Health summary cards
        dbc.Row([
            # Heart rate card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="heart-rate-summary"),
                        dcc.Graph(id="heart-rate-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
            
            # Sleep card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Sleep", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="sleep-summary"),
                        dcc.Graph(id="sleep-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
            
            # HRV card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Variability", className="card-title")),
                    dbc.CardBody([
                        html.Div(id="hrv-summary"),
                        dcc.Graph(id="hrv-chart", style={"height": "200px"})
                    ])
                ])
            ], width=12, lg=4, className="mb-4"),
        ]),
        
        # Detailed charts
        dbc.Row([
            # Heart rate zones chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Heart Rate Zones", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="heart-rate-zones-chart", style={"height": "300px"})
                    ])
                ])
            ], width=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Activity Trends", className="card-title")),
                    dbc.CardBody([
                        dcc.Graph(id="activity-chart", style={"height": "300px"})
                    ])
                ])
            ], width=6, className="mb-4"),
        ]),
        
        # Footer
        create_footer()
    ], fluid=True)

@callback(
    [Output("participant-start-date", "date"),
     Output("participant-end-date", "date")],
    [Input("btn-last-7-days", "n_clicks"),
     Input("btn-last-30-days", "n_clicks"),
     Input("btn-this-month", "n_clicks")],
    [State("participant-start-date", "date"),
     State("participant-end-date", "date")],
    prevent_initial_call=True
)
def update_date_range(n_last_7, n_last_30, n_this_month, current_start, current_end):
    """Update the date range based on button clicks"""
    ctx = callback_context
    
    if not ctx.triggered:
        return current_start, current_end
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    today = datetime.now().date()
    
    if button_id == "btn-last-7-days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif button_id == "btn-last-30-days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif button_id == "btn-this-month":
        start_date = today.replace(day=1)
        end_date = today
    else:
        return current_start, current_end
    
    return start_date, end_date

@callback(
    [Output("heart-rate-summary", "children"),
     Output("heart-rate-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_heart_rate_info(start_date, end_date):
    """Update heart rate information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                annotations=[dict(
                    text="No data available for the selected date range",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=200
            )
            
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_resting_hr = df['resting_hr'].mean()
        max_hr = df['max_hr'].max()
        min_hr = df['resting_hr'].min()
        
        # Create summary card
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_resting_hr:.0f}", className="text-primary text-center"),
                    html.P("Avg Resting HR", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{max_hr:.0f}", className="text-danger text-center"),
                    html.P("Max HR", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{min_hr:.0f}", className="text-success text-center"),
                    html.P("Min HR", className="text-muted text-center small"),
                ], width=4),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add resting heart rate line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['resting_hr'],
            mode='lines+markers',
            name='Resting HR',
            line=dict(color='#1976D2', width=2),
            marker=dict(size=6)
        ))
        
        # Add max heart rate line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['max_hr'],
            mode='lines+markers',
            name='Max HR',
            line=dict(color='#D32F2F', width=2, dash='dot'),
            marker=dict(size=6)
        ))
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="BPM"
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(
                text=f"Error loading data: {str(e)}",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=200
        )
        
        return html.Div("No data available"), empty_fig

@callback(
    [Output("sleep-summary", "children"),
     Output("sleep-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_sleep_info(start_date, end_date):
    """Update sleep information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                annotations=[dict(
                    text="No data available for the selected date range",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=200
            )
            
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_sleep = df['sleep_hours'].mean()
        min_sleep = df['sleep_hours'].min()
        max_sleep = df['sleep_hours'].max()
        
        # Create summary card
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_sleep:.1f}", className="text-primary text-center"),
                    html.P("Avg Hours", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{min_sleep:.1f}", className="text-danger text-center"),
                    html.P("Min Hours", className="text-muted text-center small"),
                ], width=4),
                dbc.Col([
                    html.H3(f"{max_sleep:.1f}", className="text-success text-center"),
                    html.P("Max Hours", className="text-muted text-center small"),
                ], width=4),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add sleep hours bars
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['sleep_hours'],
            marker_color='#4CAF50',
            text=df['sleep_hours'].round(1),
            textposition="outside"
        ))
        
        # Add recommended sleep range
        fig.add_shape(
            type="rect",
            x0=df['date'].min(),
            x1=df['date'].max(),
            y0=7,
            y1=9,
            fillcolor="rgba(0,200,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="Hours",
            range=[0, max(10, max_sleep * 1.1)]
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(
                text=f"Error loading data: {str(e)}",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=200
        )
        
        return html.Div("No data available"), empty_fig

@callback(
    [Output("hrv-summary", "children"),
     Output("hrv-chart", "figure")],
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_hrv_info(start_date, end_date):
    """Update HRV information and chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                annotations=[dict(
                    text="No data available for the selected date range",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=200
            )
            
            return html.Div("No data available"), empty_fig
        
        # Calculate summary statistics
        avg_hrv = df['hrv_rest'].mean()
        trend = df['hrv_rest'].iloc[-1] - df['hrv_rest'].iloc[0] if len(df) > 1 else 0
        trend_pct = (trend / df['hrv_rest'].iloc[0]) * 100 if len(df) > 1 and df['hrv_rest'].iloc[0] > 0 else 0
        
        # Create summary card
        trend_color = "text-success" if trend > 0 else "text-danger"
        trend_icon = "↑" if trend > 0 else "↓"
        
        summary = html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3(f"{avg_hrv:.0f}", className="text-primary text-center"),
                    html.P("Avg HRV (ms)", className="text-muted text-center small"),
                ], width=6),
                dbc.Col([
                    html.H3([
                        f"{trend_icon} {abs(trend_pct):.1f}%"
                    ], className=f"{trend_color} text-center"),
                    html.P("Trend", className="text-muted text-center small"),
                ], width=6),
            ]),
        ])
        
        # Create chart
        fig = go.Figure()
        
        # Add HRV line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['hrv_rest'],
            mode='lines+markers',
            line=dict(color='#673AB7', width=2),
            marker=dict(size=6)
        ))
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            template="plotly_white",
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(
            title_text="",
            tickformat="%b %d",
            tickangle=-45
        )
        
        fig.update_yaxes(
            title_text="HRV (ms)"
        )
        
        return summary, fig
    except Exception as e:
        # Return empty states in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(
                text=f"Error loading data: {str(e)}",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=200
        )
        
        return html.Div("No data available"), empty_fig

@callback(
    Output("heart-rate-zones-chart", "figure"),
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_heart_rate_zones_chart(start_date, end_date):
    """Update heart rate zones chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                annotations=[dict(
                    text="No data available for the selected date range",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=300
            )
            
            return empty_fig
        
        # Extract zone columns and calculate averages
        zone_cols = [f'zone{i}_percent' for i in range(1, 8)]
        zone_avgs = df[zone_cols].mean().reset_index()
        zone_avgs.columns = ['zone', 'percentage']
        zone_avgs['zone'] = zone_avgs['zone'].apply(lambda x: f"Zone {x[-1]}")
        
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
        
        zone_avgs['description'] = zone_avgs['zone'].map(zone_desc)
        zone_avgs['hover_text'] = zone_avgs.apply(
            lambda row: f"{row['zone']}: {row['percentage']:.1f}%<br>{row['description']}", 
            axis=1
        )
        
        # Colors for zones
        colors = ["#80d8ff", "#4dd0e1", "#26c6da", "#26a69a", "#9ccc65", "#ffee58", "#ffab91"]
        
        # Create chart
        fig = go.Figure()
        
        # Add pie chart
        fig.add_trace(go.Pie(
            labels=zone_avgs['zone'],
            values=zone_avgs['percentage'],
            text=zone_avgs['description'],
            hovertext=zone_avgs['hover_text'],
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
    except Exception as e:
        # Return empty chart in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(
                text=f"Error loading data: {str(e)}",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=300
        )
        
        return empty_fig

@callback(
    Output("activity-chart", "figure"),
    [Input("participant-start-date", "date"),
     Input("participant-end-date", "date")]
)
def update_activity_chart(start_date, end_date):
    """Update activity chart"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
        raise PreventUpdate
    
    user_id = current_user.id
    
    try:
        # Load data from database
        df = load_participant_data(user_id, start_date, end_date)
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                annotations=[dict(
                    text="No data available for the selected date range",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=300
            )
            
            return empty_fig
        
        # Create chart
        fig = go.Figure()
        
        # Add steps bars
        # fig.add_trace(go.Bar(
        #     x=df['date'],
        #     y=df['steps'],
        #     name='Steps',
        #     marker_color='#3F51B5',
        #     yaxis='y'
        # ))
        
        # Update layout for dual axis
        # fig.update_layout(
        #     title="Daily Activity",
        #     xaxis=dict(
        #         title="Date",
        #         tickformat="%b %d",
        #         tickangle=-45
        #     ),
        #     yaxis=dict(
        #         title="Steps",
        #         titlefont=dict(color='#3F51B5'),
        #         tickfont=dict(color='#3F51B5')
        #     ),
        #     yaxis2=dict(
        #         title="Calories",
        #         titlefont=dict(color='#F44336'),
        #         tickfont=dict(color='#F44336'),
        #         anchor="x",
        #         overlaying="y",
        #         side="right"
        #     ),
        #     margin=dict(l=60, r=60, t=50, b=50),
        #     height=300,
        #     template="plotly_white",
        #     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        # )
        
        return fig
    except Exception as e:
        # Return empty chart in case of error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            annotations=[dict(
                text=f"Error loading data: {str(e)}",
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14)
            )],
            height=300
        )
        
        return empty_fig