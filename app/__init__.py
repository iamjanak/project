from flask import Flask
from .routes import main

def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )


    app.secret_key = "hospital-secret-key"


    from app.routes import main

    app.register_blueprint(main)


    return app