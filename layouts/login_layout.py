from dash import html, clientside_callback, ClientsideFunction, Output, Input
import dash_bootstrap_components as dbc

def create_enter_key_callback():
    clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='handleEnterKey'
        ),
        Output('login-button', 'n_clicks', allow_duplicate=True),
        Input('password-input', 'n_submit'),
        prevent_initial_call=True
    )


layout = dbc.Container(
    [
        html.H1("FitonDuty Dashboard - Login", className="text-center my-4"),
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
                                className="mb-3",
                                n_submit=0
                            ),
                            dbc.Input(
                                id="password-input", 
                                placeholder="Password", 
                                type="password",
                                className="mb-3",
                                n_submit=0
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
                xs={"size": 12, "offset": 0},  # Full width on extra small screens
                sm={"size": 10, "offset": 1},  # 10/12 width on small screens
                md={"size": 6, "offset": 3},   # 6/12 width on medium screens
                lg={"size": 4, "offset": 4},   # 4/12 width on large screens
            )
        )
    ],
    fluid=True,
    className="vh-100 d-flex flex-column justify-content-center"
)

create_enter_key_callback()