# layouts/admin_layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user
from datetime import datetime

# Import modular components
from components.admin.sidebar import create_admin_sidebar
from components.admin.group_comparison import create_group_comparison
from components.admin.group_summary import create_group_summary
from components.admin.participant_detail import create_participant_detail
from layouts.footer import create_footer

def create_layout():
    """
    Create the admin dashboard layout with full-height sidebar and no navbar
    
    Returns:
        A dash component with the admin dashboard
    """
    # Complete admin layout with full-height sidebar and no navbar
    return html.Div([
        # Main container with sidebar and content
        html.Div([
            # Sidebar - extends full height
            html.Div([
                # Sidebar Header
                html.Div([
                    html.Img(src="/assets/logo.svg", height="40px", className="mb-2"),
                    html.H4("FitonDuty", className="text-primary mb-0"),
                    html.Div(id="admin-user-info", className="text-center my-2"),
                ], className="sidebar-header text-center"),
                
                # Sidebar Content
                html.Div(
                    create_admin_sidebar(),
                    className="sidebar-content p-3",
                ),
            ],
            id="sidebar-column",
            className="sidebar-column px-0",
            ),
            
            # Toggle button container (separate from sidebar)
            html.Div(
                html.Button(
                    "❮", # Left arrow (default when sidebar is open)
                    id="sidebar-toggle",
                    className="sidebar-toggle-btn",
                ),
                id="sidebar-toggle-container",
                className="sidebar-toggle-container",
            ),
            
            # Main content area - KEEP ID CONSISTENT WITH CALLBACKS 
            html.Div([
                # Main content with title but no navbar
                html.Div([
                    # Dashboard title
                    html.H2("FitonDuty Dashboard", className="dashboard-title"),
                    
                    # Selected view information
                    html.Div(id="selected-view-info", className="mb-4"),
                    
                    # Data visualization sections
                    html.Div(id="admin-data-visualizations"),
                    
                    # Add a Store component to hold the selected participant ID
                    dcc.Store(id="selected-participant-store")
                ], className="main-content-container"),
                
                # Footer
                create_footer()
            ],
            id="main-content-column",  # Keep this ID as it's used in callbacks
            className="main-content-column",
            ),
        ],
        className="dashboard-container",
        ),
        
        # Store to track sidebar state
        dcc.Store(id="sidebar-state", data={"is_open": True})
    ])