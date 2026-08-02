from flask import Flask
from flask_migrate import Migrate

from .database import db
from config import Config


migrate = Migrate()


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )


    app.secret_key = "hospital-secret-key"


    # Load database configuration
    app.config.from_object(Config)


    # Initialize database
    db.init_app(app)


    # Initialize migration
    migrate.init_app(app, db)


    # Load models
    from app import models


    # Register routes
    from app.routes import main

    app.register_blueprint(main)


    return app


__all__ = ["db", "create_app"]