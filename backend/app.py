import os
import secrets
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

    from routes import main_bp

    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=7654, debug=True)
