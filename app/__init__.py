# app/__init__.py
import os
from flask import Flask
from mongoengine import connect
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev")

    # Always connect using MONGODB_URI
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI not set in .env")
    
    connect(host=mongo_uri)

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
