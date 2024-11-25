from flask import Flask
from flask_cors import CORS
from .routes import main  # Import your blueprint
from .config import db  # Import configured database
from .config import client
from pymongo.errors import ConnectionFailure

def create_app():
    app = Flask(__name__)

    try:
       # CORS(app, resources={r"/*": {"origins": "*"}})
        # Test the MongoDB connection
        client.admin.command('ping')  # Ping the database to ensure it's connected
        app.mongo_db = db  # Set the db connection to Flask app
    except ConnectionFailure:
        print("MongoDB connection failed!")
        raise

    # Register blueprints
    app.register_blueprint(main)

    return app

