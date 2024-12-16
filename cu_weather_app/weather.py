from cu_weather_app.api import (
    get_location_key,
    get_weather_data,
    parse_error_code,
)

from flask import current_app
import requests
from flask import (
    Blueprint,
    render_template,
    request,
)

bp = Blueprint("weather", __name__, url_prefix="/weather")


@bp.route("/", methods=("GET", "POST"))
def weather():
    if request.method == "GET":
        return render_template("weather.html")

    start_city = request.form.get("start_city")
    end_city = request.form.get("end_city")

    try:
        start_location_key = get_location_key(start_city)
        end_location_key = get_location_key(end_city)
    except (ConnectionError, TimeoutError) as e:
        current_app.logger.error(e)
        return render_template(
            "weather.html", error="Сервис погоды не доступен в данный момент"
        )
    except requests.exceptions.HTTPError as e:
        current_app.logger.error(e)
        return render_template(
            "weather.html", error=parse_error_code(e.response.status_code)
        )

    if not start_location_key:
        return render_template("weather.html", error=f"Город {start_city} не найден")
    if not end_location_key:
        return render_template("weather.html", error=f"Город {end_city} не найден")

    current_app.logger.info(f"start location key = '{start_location_key}'")
    current_app.logger.info(f"end location key = '{end_location_key}'")

    # start_location_key = 294021  # Москва
    # end_location_key = 290150  # Якутск

    try:
        start_weather_data = get_weather_data(start_location_key)
        end_weather_data = get_weather_data(end_location_key)
    except (ConnectionError, TimeoutError) as e:
        current_app.logger.error(e)
        return render_template(
            "weather.html", error="Сервис погоды не доступен в данный момент"
        )
    except requests.exceptions.HTTPError as e:
        return render_template(
            "weather.html", error=parse_error_code(e.response.status_code)
        )

    if not start_weather_data or not end_weather_data:
        return render_template(
            "weather.html", error="Не удалось получить данные о погоде"
        )

    start_conditions = parse_weather_conditions(start_weather_data)
    end_conditions = parse_weather_conditions(end_weather_data)

    start_result = check_bad_weather(**start_conditions)
    end_result = check_bad_weather(**end_conditions)

    return render_template(
        "weather.html",
        result=f"Погода в {start_city}: {start_result}. Погода в {end_city}: {end_result}.",
    )


def check_bad_weather(temperature, wind_speed, precipitation_probability, humidity):
    if (
        temperature <= 0
        or temperature >= 35
        or wind_speed >= 50
        or precipitation_probability >= 70
        or humidity >= 90
    ):
        return "Плохие погодные условия"
    else:
        return "Хорошие погодные условия"


def parse_weather_conditions(weather_data):
    conditions = weather_data["DailyForecasts"][0]
    return {
        "temperature": conditions["Temperature"]["Maximum"]["Value"],
        "wind_speed": conditions["Day"]["Wind"]["Speed"]["Value"],
        "precipitation_probability": conditions["Day"]["PrecipitationProbability"],
        "humidity": conditions["Day"]["RelativeHumidity"]["Average"],
    }
