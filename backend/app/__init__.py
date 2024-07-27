from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py', silent=True)

    # Import and register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

