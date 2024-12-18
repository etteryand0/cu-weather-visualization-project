import os

import aiohttp
import requests


async def get_location_key(city_name, *, session=None):
    url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {"apikey": os.environ["ACCUWEATHER_API_KEY"], "q": city_name}

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


def get_weather_data(location_key):
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {
        "apikey": os.environ["ACCUWEATHER_API_KEY"],
        "details": "true",
        "metric": "true",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


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
