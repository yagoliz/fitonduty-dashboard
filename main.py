from app import app
import index

# Import callbacks
from callbacks import admin_callbacks, participant_callbacks

# Import components
import components.admin.sidebar
import components.admin.group_comparison
import components.admin.group_summary
import components.admin.participant_detail
import components.participant.date_selector
import components.participant.health_metrics
import components.participant.detailed_charts

# Start the server
if __name__ == '__main__':
    app.run(debug=True)