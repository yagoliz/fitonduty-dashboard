from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container(
    [
        html.H1("Healthcare Dashboard - Login", className="text-center my-4"),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H3("Sign In", className="text-center"),
                            dbc.Input(
                                id="username-input", 
                                placeholder="Username", 
                                type="text",
                                className="mb-3"
                            ),
                            dbc.Input(
                                id="password-input", 
                                placeholder="Password", 
                                type="password",
                                className="mb-3"
                            ),
                            dbc.Button(
                                "Login", 
                                id="login-button", 
                                color="primary", 
                                className="w-100"
                            ),
                            html.Div(id="login-status", className="mt-3")
                        ]
                    )
                ),
                width={"size": 6, "offset": 3},
                md={"size": 4, "offset": 4},
            )
        )
    ],
    fluid=True,
    className="vh-100 d-flex flex-column justify-content-center"
)