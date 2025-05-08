from app import app, server as application

# Now import index which registers routes
import index

# Import all callbacks to ensure they're registered
from callbacks import admin_callbacks, participant_callbacks

# Import components that might register callbacks
import components.admin.sidebar
import components.admin.group_comparison
import components.admin.group_summary
import components.admin.participant_detail
import components.participant.date_selector
import components.participant.health_metrics
import components.participant.detailed_charts

# Now the application is fully initialized and can be served by Gunicorn
if __name__ == "__main__":
    application.run()