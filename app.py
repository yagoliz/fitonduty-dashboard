import dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask import Flask, request
from werkzeug.security import check_password_hash
import uuid
import os
from datetime import datetime, timedelta
from utils.database import get_user_by_username, update_last_login, create_session, get_user_groups, get_user_by_id

# Initialize the Flask server
server = Flask(__name__)
server.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
server.config['SESSION_COOKIE_SECURE'] = os.environ.get('ENV', 'development') == 'production'
server.config['SESSION_COOKIE_HTTPONLY'] = True
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialize the Dash app with the Flask server
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="FitonDuty | Dashboard",
)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# User class that works with our database
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.role = user_data.get('role', 'participant')
        
        # Load groups for user (for participants)
        self._groups = None
        
    @property
    def groups(self):
        # Lazy load groups when needed
        if self._groups is None and self.role == 'participant':
            self._groups = get_user_groups(self.id)
        return self._groups
    
    @property 
    def group(self):
        # For backward compatibility - returns the first group name
        groups = self.groups
        if groups and len(groups) > 0:
            return groups[0]['group_name']
        return None
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_participant(self):
        return self.role == 'participant'
    
    @property
    def display_name(self):
        return self.username
    
    def check_password(self, password):
        # Get fresh user data to check password
        user_data = get_user_by_username(self.username)
        if user_data:
            return check_password_hash(user_data['password_hash'], password)
        return False

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID from database"""
    try:
        # Convert string ID to integer
        user_id = int(user_id)
        
        # Get user from database
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Custom login function
def login_and_create_session(user):
    """Log in user and create a session record"""
    try:
        login_user(user)
        
        # Update last login timestamp
        update_last_login(user.id)
        
        # Create a session record
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=1)
        
        # Get request details
        ip_address = request.remote_addr
        user_agent = request.user_agent.string
        
        # Create session in database
        create_session(user.id, session_token, ip_address, user_agent, expires_at)
        
        return True
    except Exception as e:
        print(f"Error during login: {e}")
        return False