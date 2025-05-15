from app import app
import index

# Import callbacks
from callbacks import admin_callbacks, participant_callbacks


# Start the server
if __name__ == '__main__':
    app.run(debug=True)