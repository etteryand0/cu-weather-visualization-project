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
