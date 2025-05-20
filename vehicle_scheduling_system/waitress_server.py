from waitress import serve
from app import create_app
import logging
from logging.handlers import RotatingFileHandler
import sys
from flask_cors import CORS

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('waitress')

def configure_logging():
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # File handler (rotating logs)
    fh = RotatingFileHandler('scheduler.log', maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    
    logger.addHandler(ch)
    logger.addHandler(fh)

def run_server():
    try:
        # Explicitly create production app
        application = create_app('production')
        
        # Apply CORS to the application
        CORS(application, resources={r"/*": {"origins": "*"}})
        logger.info("CORS enabled for all origins")
        
        host = '0.0.0.0'
        port = 8080
        threads = 4
        
        logger.info("Application initialization complete")
        logger.info(f"Starting Waitress server on {host}:{port}")
        logger.info(f"Thread workers: {threads}")
        
        serve(
            application,
            host=host,
            port=port,
            threads=threads,
            ident=None,  # Hide server banner
            _quiet=False  # Ensure Waitress logs are visible
        )
    except Exception as e:
        logger.error(f"Server failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    configure_logging()  # Call the logging configuration function
    run_server()