from waitress import serve
from app import create_app

application = create_app()

if __name__ == '__main__':
    print("Starting waitress server on http://0.0.0.0:5000")
    serve(application, host='0.0.0.0', port=8080, threads=4)