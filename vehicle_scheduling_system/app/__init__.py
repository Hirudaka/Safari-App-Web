# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo.errors import ConnectionFailure
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration classes defined directly in this file
class DefaultConfig:
    DEBUG = True
    TESTING = False
    MONGODB_DATABASE = 'dev_db'
    SECRET_KEY = 'dev-secret-key'
    ALLOWED_ORIGINS = ['*']

class ProductionConfig(DefaultConfig):
    DEBUG = False
    MONGODB_DATABASE = 'prod_db'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-production-key')
    ALLOWED_ORIGINS = [os.environ.get('ALLOWED_ORIGIN', 'https://yourdomain.com')]

class TestingConfig(DefaultConfig):
    TESTING = True
    MONGODB_DATABASE = 'test_db'

def create_app(config_name=None):
    """
    Application factory function to create and configure the Flask app
    
    Args:
        config_name (str): Configuration environment ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration based on environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
        # Restrict CORS in production
        CORS(app, resources={r"/*": {"origins": app.config.get('ALLOWED_ORIGINS', [])}})
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
        CORS(app)  # Permissive for testing
    else:  # development is default
        app.config.from_object(DefaultConfig)
        # Allow all origins in development
        CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure MongoDB
    try:
        from .config import client, db  # Import directly from your existing config module
        # Test the MongoDB connection
        client.admin.command('ping')
        app.mongo_db = db  # Set the db connection to Flask app
        logger.info("MongoDB connected successfully!")
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise
    except ImportError as e:
        logger.error(f"Failed to import MongoDB configuration: {e}")
        raise
    
    # Register health check route
    @app.route('/health')
    def health_check():
        """Simple health check endpoint to verify app and DB status"""
        try:
            client.admin.command('ping')
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "environment": config_name
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }), 500
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        from .routes import main  # Import your existing blueprint
        app.register_blueprint(main)
        
        # Register additional blueprints as needed
        # from .routes.auth import auth_bp
        # app.register_blueprint(auth_bp, url_prefix='/auth')
        
        logger.info("Blueprints registered successfully")
    except ImportError as e:
        logger.error(f"Failed to register blueprints: {e}")
        raise

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400
    
    logger.info("Error handlers registered")

# Run the application (for development)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)