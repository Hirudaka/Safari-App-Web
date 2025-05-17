from app import create_app

# This is the WSGI entry point for production servers like Gunicorn
application = create_app()

if __name__ == "__main__":
    application.run()