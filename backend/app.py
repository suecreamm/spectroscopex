from flask import Flask
from flask_cors import CORS
from error_handlers import register_error_handlers
from routes import main_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(main_bp)
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=7654, debug=True)