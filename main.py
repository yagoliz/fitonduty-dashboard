from app import app
import index # noqa: F401

# Import callbacks
from callbacks import admin_callbacks, participant_callbacks, supervisor_callbacks # noqa: F401


# Start the server
if __name__ == '__main__':
    app.run(debug=True)