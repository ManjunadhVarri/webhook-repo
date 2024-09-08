from flask import Flask
from app.webhook.routes import webhook  # Adjust the import based on your folder structure
from app.config import Config
from app.extension import mongo

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    mongo.init_app(app)
    
    # Register blueprints
    app.register_blueprint(webhook)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
