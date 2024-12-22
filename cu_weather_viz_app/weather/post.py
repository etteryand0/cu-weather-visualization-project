from cu_weather_viz_app.weather.utils import check_bad_weather, parse_weather_conditions
from cu_weather_viz_app.api import (
    get_location_key,
    parse_error_code,
)
from . import bp

import asyncio
import aiohttp
from flask import current_app
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
            [city.strip() for city in request.form.get("pitstop_cities").split(",")],
        )
    )

    async with aiohttp.ClientSession() as session:
        coroutines = [
            get_location_key(city, session=session)
            for city in [start_city, *pitstop_cities, end_city]
        ]

        try:
            result = await asyncio.gather(*coroutines)
        except (ConnectionError, TimeoutError) as e:
            current_app.logger.error(e)
            return render_template(
                "weather.html", error="Сервис погоды не доступен в данный момент"
            )
        except aiohttp.ClientResponseError as e:
            current_app.logger.error(e)
            return render_template("weather.html", error=parse_error_code(e.status))

    location_keys = [key for key, _ in result]
    locations = [location for _, location in result]
    for i, city_name in enumerate([start_city, *pitstop_cities, end_city]):
        locations[i]["name"] = city_name

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

    cities = list(zip(location_keys, [start_city, *pitstop_cities, end_city]))

    return render_template("result.html", cities=cities, locations=locations)
