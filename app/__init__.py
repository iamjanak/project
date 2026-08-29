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

    # =====================================================
    # DATABASE
    # =====================================================

    db.init_app(app)

    migrate.init_app(app, db)

    # =====================================================
    # LOAD MODELS
    # =====================================================

    from app import models

    # =====================================================
    # MAIN ROUTES
    # =====================================================

    from app.routes import main

    # =====================================================
    # FOLLOW-UP ROUTES
    # =====================================================

    from app.followup_routes import followup_bp

    # =====================================================
    # PATIENT INFO CORRECTION ROUTES
    # =====================================================

    from app.patient_correction import patient_correction

    # =====================================================
    # WARD ROUTES
    # =====================================================

    from app.ward_routes import ward_bp

    # =====================================================
    # ROOM ROUTES
    # =====================================================

    from app.room_routes import room_bp

    # =====================================================
    # BED ROUTES
    # =====================================================

    from app.bed import bed_bp

    # =====================================================
    # PATIENT ADMISSION ROUTES
    # =====================================================

    from app.admission_routes import admission_bp

    # =====================================================
    # REGISTER BLUEPRINTS
    # =====================================================

    app.register_blueprint(main)

    app.register_blueprint(followup_bp)

    app.register_blueprint(patient_correction)

    app.register_blueprint(ward_bp)

    app.register_blueprint(room_bp)

    app.register_blueprint(bed_bp)

    app.register_blueprint(admission_bp)

    return app


__all__ = [
    "db",
    "create_app"
]