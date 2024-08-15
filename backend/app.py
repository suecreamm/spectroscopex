from flask import Flask
from flask_cors import CORS
from routes import main_bp
from error_handlers import register_error_handlers
import os
import secrets

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

    app.register_blueprint(main_bp)
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=7654, debug=True)
