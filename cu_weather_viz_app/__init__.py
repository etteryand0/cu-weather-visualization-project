import os

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping()

    if os.environ.get("ACCUWEATHER_API_KEY") is None:
        raise Exception("ACCUWEATHER_API_KEY env variable not set")

    from . import weather

    app.register_blueprint(weather.bp, url_prefix="")

    return app
