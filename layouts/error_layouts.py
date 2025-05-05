from dash import html
import dash_bootstrap_components as dbc

# Not Found layout
not_found_layout = dbc.Container(
    [
        html.H1("404 - Not Found", className="text-center my-5 text-danger"),
        html.Div(
            [
                html.P("The page you are looking for does not exist."),
                dbc.Button(
                    "Return to Home",
                    id="return-home-button",
                    color="primary",
                    className="mt-3",
                    href="/",
                ),
            ],
            className="text-center",
        ),
    ],
    fluid=True,
    className="vh-100 d-flex flex-column justify-content-center",
)

# Forbidden layout
forbidden_layout = dbc.Container(
    [
        html.H1("403 - Forbidden", className="text-center my-5 text-danger"),
        html.Div(
            [
                html.P("You don't have permission to access this page."),
                dbc.Button(
                    "Return to Home",
                    id="return-home-button-forbidden",
                    color="primary",
                    className="mt-3",
                    href="/",
                ),
            ],
            className="text-center",
        ),
    ],
    fluid=True,
    className="vh-100 d-flex flex-column justify-content-center",
)

# Server Error layout
server_error_layout = dbc.Container(
    [
        html.Div(
            [
                html.H1("500 - Server Error", className="text-danger"),
                html.H3("Something Went Wrong"),
                html.P(
                    "The server encountered an error and could not complete your request."
                ),
                html.Hr(),
                dbc.Button("Return to Dashboard", href="/", color="primary"),
            ],
            className="text-center p-5",
        )
    ],
    className="vh-100 d-flex flex-column justify-content-center",
)
