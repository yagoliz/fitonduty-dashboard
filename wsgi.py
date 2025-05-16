from app import app, server as application # noqa: F401

# Now import index which registers routes
import index # noqa: F401

# Import all callbacks to ensure they're registered
from callbacks import admin_callbacks, participant_callbacks  # noqa: F401


# Now the application is fully initialized and can be served by Gunicorn
if __name__ == "__main__":
    application.run()