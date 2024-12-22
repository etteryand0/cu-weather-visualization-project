import os
import locale

from flask import Flask


from .dash_app import create_dash_app

locale.setlocale(locale.LC_TIME, "rus")


def create_app():
    app = Flask(__name__)
    app.config.from_mapping()

    if os.environ.get("ACCUWEATHER_API_KEY") is None:
        raise Exception("ACCUWEATHER_API_KEY env variable not set")

    dash_app = create_dash_app(app)

    @app.route("/dash")
    def dash_endpoint():
        return dash_app.index()

    from . import weather

    app.register_blueprint(weather.bp, url_prefix="")

    return app
