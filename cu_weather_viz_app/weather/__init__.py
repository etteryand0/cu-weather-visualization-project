from flask import Blueprint

bp = Blueprint("weather", __name__, url_prefix="/")

# Импортируется после bp для избежания цикла
from . import view, post
