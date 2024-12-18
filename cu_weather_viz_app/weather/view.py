from . import bp

from flask import render_template


@bp.route("/", methods=("GET",))
def weather():
    return render_template("weather.html")
