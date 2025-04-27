from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    from .routes import app_routes
    app.register_blueprint(app_routes)

    return app
