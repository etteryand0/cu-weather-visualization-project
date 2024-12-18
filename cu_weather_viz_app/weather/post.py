from cu_weather_viz_app.weather.utils import check_bad_weather, parse_weather_conditions
from cu_weather_viz_app.api import (
    get_location_key,
    get_weather_data,
    parse_error_code,
)
from . import bp

import asyncio
import aiohttp
from flask import current_app
import requests
from flask import (
    render_template,
    request,
)


@bp.route("/", methods=("POST",))
async def query_weather():
    start_city = request.form.get("start_city")
    end_city = request.form.get("end_city")
    pitstop_cities = list(
        filter(
            lambda city: len(city) > 3,
            [city.strip() for city in request.form.get("pitstop_cities").split(" ")],
        )
    )

    async with aiohttp.ClientSession() as session:
        coroutines = [
            get_location_key(city, session=session)
            for city in [start_city, *pitstop_cities, end_city]
        ]

        try:
            location_keys = await asyncio.gather(*coroutines)
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

    missing_cities = list(
        filter(
            lambda data: data[1] is None,
            zip([start_city, *pitstop_cities, end_city], location_keys),
        )
    )
    if len(missing_cities) == 1:
        return render_template(
            "weather.html", error=f"Город {missing_cities[0][0]} не найден"
        )
    elif len(missing_cities) > 1:
        return render_template(
            "weather.html",
            error=f"Города {', '.join([city for city, _ in missing_cities])} не найдены",
        )

    start_location_key, *pitstop_location_keys, end_location_key = location_keys

    current_app.logger.info(f"start location key = '{start_location_key}'")
    current_app.logger.info(
        f"pitstop_location_keys = '{', '.join(pitstop_location_keys)}'"
    )
    current_app.logger.info(f"end location key = '{end_location_key}'")

    # start_location_key = 294021  # Москва
    # pitstop_location_keys = [292712, 294490, 294927] # Иркутск, Орёл, Владивосток
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
