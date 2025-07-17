from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from utils.visualization.general_charts import create_group_data_summary_chart, create_group_daily_line_chart, create_group_physiological_line_chart, create_group_questionnaire_line_chart
from utils.logging_config import get_logger

logger = get_logger(__name__)


def create_group_data_summary_visualization(end_date, group_data, daily_data=None):
    """Create visualization for group data summary showing data amounts"""
    try:
        logger.info(f"Creating group data summary visualization - group_data: {len(group_data) if group_data else 0} records, daily_data: {len(daily_data) if daily_data else 0} records")
        
        if not group_data:
            logger.warning("No group data available for visualization")
            return html.Div([
                dbc.Alert("No group data available", color="info")
            ])
        
        # Create separate charts for physiological and questionnaire data
        if daily_data:
            logger.debug(f"Creating separate charts with {len(daily_data)} daily data points")
            physio_fig = create_group_physiological_line_chart(daily_data)
            questionnaire_fig = create_group_questionnaire_line_chart(daily_data)
        else:
            logger.warning("No daily data provided for charts")
            physio_fig = None
            questionnaire_fig = None
        
        # Create summary table for current day data
        table_data = []
        for group in group_data:
            table_data.append({
                'Group': group['group_name'],
                'Total Participants': group['total_participants'],
                'Physiological Data': group['physio_current_day_count'],
                'Questionnaire Data': group['questionnaire_current_day_count']
            })
        
        table_df = pd.DataFrame(table_data)
        
        # Create data table
        data_table = dbc.Table.from_dataframe(
            table_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size="sm"
        )
        
        # Create Cards for each component
        components = []
        
        # Summary Table Card
        summary_card = dbc.Card([
            dbc.CardHeader(html.H5(f"Current Day Data Summary - {end_date}", className="card-title")),
            dbc.CardBody([
                html.P("Number of participants with data for the selected day.", 
                       className="text-muted mb-3"),
                data_table
            ])
        ], className="mb-4")
        components.append(summary_card)
        
        # Daily Trends Chart Cards - Side by Side
        if physio_fig and questionnaire_fig:
            # Create a row with two charts side by side
            charts_row = dbc.Row([
                # Physiological Data Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Physiological Data Trends", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    figure=physio_fig,
                                    config={
                                        'displayModeBar': False,
                                        'responsive': True
                                    },
                                    className="chart-container",
                                    style={"height": "100%", "width": "100%"}
                                )
                            ], className="chart-wrapper", style={"height": "400px"})
                        ])
                    ])
                ], width=12, lg=6, className="mb-4"),
                
                # Questionnaire Data Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Questionnaire Data Trends", className="card-title")),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    figure=questionnaire_fig,
                                    config={
                                        'displayModeBar': False,
                                        'responsive': True
                                    },
                                    className="chart-container",
                                    style={"height": "100%", "width": "100%"}
                                )
                            ], className="chart-wrapper", style={"height": "400px"})
                        ])
                    ])
                ], width=12, lg=6, className="mb-4")
            ])
            components.append(charts_row)
            
            # Add legend below the charts
            components.append(
                html.Div([
                    html.P([
                        html.Strong("Chart Legend: "),
                        html.Span("Shows daily data availability trends over the selected date range")
                    ], className="text-muted small text-center")
                ], className="mb-4")
            )
        else:
            components.append(
                dbc.Card([
                    dbc.CardHeader(html.H5("Daily Data Availability Trends", className="card-title")),
                    dbc.CardBody([
                        dbc.Alert("No daily data available for line charts", color="info")
                    ])
                ], className="mb-4")
            )
        
        return html.Div(components)
        
    except Exception as e:
        logger.error(f"Error creating group data summary visualization: {e}", exc_info=True)
        return html.Div([
            dbc.Alert(f"Error creating visualization: {str(e)}", color="danger")
        ])