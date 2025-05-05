# layouts/footer.py
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime

def create_footer():
    current_year = datetime.now().year
    
    footer = html.Footer(
        dbc.Container(
            [
                html.P(
                    [
                        f"Copyright © {current_year} | CYD Campus x BASPO"
                    ],
                    className="text-center text-muted"
                )
            ],
            fluid=True
        ),
        className="mt-auto py-3"
    )
    
    return footer