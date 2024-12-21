import os
from datetime import datetime

import aiohttp


async def get_location_key(city_name, *, session=None):
    """
    Получить location_key для запроса прогноза по названию города
    """

    url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {
        "apikey": os.environ["ACCUWEATHER_API_KEY"],
        "q": city_name,
        "language": "ru-RU",
    }

    if session is not None:
        response = await session.get(url, params=params)
        response.raise_for_status()
        data = await response.json()
    else:
        async with aiohttp.ClientSession() as s:
            response = await s.get(url, params=params)
            response.raise_for_status()
            data = await response.json()
    if data:
        return data[0]["Key"]
    return None


async def get_forecast(location_key, days: int, *, session=None):
    """
    Получить предсказание погоды на 1 или 5 вперёд
    """

    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}"
    params = {
        "apikey": os.environ["ACCUWEATHER_API_KEY"],
        "details": "true",
        "language": "ru-RU",
        "metric": "true",
    }
    if session is not None:
        response = await session.get(url, params=params)
        response.raise_for_status()
        return await response.json()

    async with aiohttp.ClientSession() as s:
        response = await s.get(url, params=params)
        response.raise_for_status()
        return await response.json()


def parse_forecast(forecast):
    return {
        "date": datetime.fromisoformat(forecast["Date"]).strftime("%A, %d %b %Y г."),
        "day_temperature": forecast["Temperature"]["Maximum"]["Value"],
        "night_temperature": forecast["Temperature"]["Minimum"]["Value"],
        "wind_speed": forecast["Day"]["Wind"]["Speed"]["Value"],
        "precipitation_probability": forecast["Day"]["PrecipitationProbability"],
        "humidity": forecast["Day"]["RelativeHumidity"]["Average"],
    }


def parse_error_code(status_code):
    match status_code:
        case 400:
            return "Сервис погоды получил некорректные данные"
        case 401:
            return "Сервис погоды не распознал API ключ нашего веб-приложения"
        case 403:
            return "Превышен лимит запросов сервиса погоды"
        case _:
            return "Сервис погоды не доступен в данный момент"
