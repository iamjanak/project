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

    # Patient Info Correction routes
    from app.patient_correction import patient_correction

    # Ward  Route
    from app.ward_routes import ward_bp
    
    # For room Route
    from app.room_routes import room_bp
    
    # For Bed Route 
    from app.bed import bed_bp
    
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(followup_bp)
    app.register_blueprint(patient_correction)
    app.register_blueprint(ward_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(bed_bp)
    
    return app


__all__ = [
    "db",
    "create_app"
]