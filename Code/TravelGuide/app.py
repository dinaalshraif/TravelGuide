import dash
from flask import Flask
import dash_bootstrap_components as dbc
# create dash app that uses bootstrap for style purposes.
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    # meta_tags allows the webapp to adapt to any screen size
    meta_tags=[{'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'}],
)
app.title ="Travel Guide"
server = app.server

