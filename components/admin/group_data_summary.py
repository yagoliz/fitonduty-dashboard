from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from utils.visualization.general_charts import create_group_data_summary_chart, create_group_daily_line_chart


def create_group_data_summary_visualization(group_data, daily_data=None):
    """Create visualization for group data summary showing data amounts"""
    try:
        print(f"DEBUG COMPONENT: group_data count: {len(group_data) if group_data else 0}")
        print(f"DEBUG COMPONENT: daily_data count: {len(daily_data) if daily_data else 0}")
        
        if not group_data:
            return html.Div([
                dbc.Alert("No group data available", color="info")
            ])
        
        # Create the line chart with daily data
        if daily_data:
            print(f"DEBUG COMPONENT: Creating line chart with {len(daily_data)} daily data points")
            fig = create_group_daily_line_chart(daily_data)
        else:
            # If no daily data, show message instead of chart
            print("DEBUG COMPONENT: No daily data provided")
            fig = None
        
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
        
        # Return combined visualization with table on top
        components = [
            html.H5("Current Day Data Summary", className="mb-3"),
            html.P("Number of participants with data for the selected day.", 
                   className="text-muted mb-3"),
            data_table,
            html.Hr(),
        ]
        
        if fig:
            components.extend([
                dcc.Graph(figure=fig),
                html.Hr(),
                html.Div([
                    html.P([
                        html.Strong("Chart Legend: "),
                        html.Span("Shows daily data availability trends over the selected date range")
                    ], className="text-muted small")
                ])
            ])
        else:
            components.append(
                dbc.Alert("No daily data available for line charts", color="info")
            )
        
        return html.Div(components)
        
    except Exception as e:
        print(f"Error creating group data summary visualization: {e}")
        return html.Div([
            dbc.Alert(f"Error creating visualization: {str(e)}", color="danger")
        ])