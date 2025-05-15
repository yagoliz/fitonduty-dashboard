from app import app, server as application

# Now import index which registers routes
import index

# Import all callbacks to ensure they're registered
from callbacks import admin_callbacks, participant_callbacks


# Now the application is fully initialized and can be served by Gunicorn
if __name__ == "__main__":
    application.run()