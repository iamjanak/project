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

    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

    # Load models
    from app import models

    # Main routes
    from app.routes import main

    # Follow-up routes
    from app.followup_routes import followup_bp

    app.register_blueprint(main)
    app.register_blueprint(followup_bp)

    return app


__all__ = [
    "db",
    "create_app"
]