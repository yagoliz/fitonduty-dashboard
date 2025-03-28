import os

import dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask server
server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize the Dash app with the Flask server
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

class User(UserMixin):
    def __init__(self, id, username, password_hash, role, group=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.group = group
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Mock user database with hashed passwords
USERS = {
    'admin': User(
        'admin', 
        'admin', 
        generate_password_hash('admin_password'),  # Replace with a strong password
        'admin'
    ),
    'participant1': User(
        'participant1', 
        'participant1', 
        generate_password_hash('participant1_password'),  # Replace with a strong password
        'participant', 
        'group1'
    ),
    'participant2': User(
        'participant2', 
        'participant2', 
        generate_password_hash('participant2_password'),  # Replace with a strong password
        'participant', 
        'group1'
    ),
    'participant3': User(
        'participant3', 
        'participant3', 
        generate_password_hash('participant3_password'),  # Replace with a strong password
        'participant', 
        'group2'
    ),
    'participant4': User(
        'participant4', 
        'participant4', 
        generate_password_hash('participant4_password'),  # Replace with a strong password
        'participant', 
        'group2'
    )
}

@login_manager.user_loader
def load_user(user_id):
    return USERS.get(user_id)