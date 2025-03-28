from dash import html
import dash_bootstrap_components as dbc
from app import USERS

def create_layout(user_id):
    # In production, you would fetch this user's specific data
    user = USERS.get(user_id)
    
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Your Health Data Dashboard", className="text-center my-4"),
                        html.Div(id="participant-info", className="mb-4"),
                        
                        # User info card
                        dbc.Card(
                            dbc.CardBody([
                                html.H4("Your Health Metrics", className="text-center"),
                                html.P(f"Welcome, {user.username}! You are in Group {user.group}"),
                                html.P("Your personal charts will be displayed here.")
                            ]),
                            className="mb-4"
                        ),
                        
                        # Logout row
                        dbc.Row(
                            dbc.Col(
                                dbc.Button(
                                    "Logout", 
                                    id="logout-button", 
                                    color="danger",
                                    className="mt-4 float-end"
                                ),
                                width=12
                            )
                        )
                    ],
                    width={"size": 10, "offset": 1},
                    lg={"size": 8, "offset": 2}
                )
            )
        ],
        fluid=True,
        className="py-4"
    )