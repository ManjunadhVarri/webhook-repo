from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    try:
        from .extension import init_db
        init_db(app)
    except Exception as e:
        print(f"Error initializing MongoDB: {str(e)}")

    from .webhook.routes import webhook
    app.register_blueprint(webhook)

    return app
