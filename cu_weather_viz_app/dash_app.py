from urllib.parse import urlparse, parse_qs

import dash
import aiohttp
import asyncio
from dash import dcc, html, Input, Output
from flask import current_app
import plotly.graph_objs as go

from .api import get_forecast, parse_forecast


def create_figs(data):
    temperature_fig = {
        "data": [
            go.Scatter(
                x=[entry["date"] for entry in data],
                y=[entry["day_temperature"] for entry in data],
                mode="lines+markers",
                name="Дневная температура (°C)",
                line=dict(color="orange"),
            ),
            go.Scatter(
                x=[entry["date"] for entry in data],
                y=[entry["night_temperature"] for entry in data],
                mode="lines+markers",
                name="Ночная температура (°C)",
                line=dict(color="blue"),
            ),
        ],
        "layout": go.Layout(
            title="Температура",
            xaxis={"title": "Дата"},
            yaxis={"title": "Температура (°C)"},
            hovermode="closest",
        ),
    }
    wind_humidity_fig = {
        "data": [
            go.Bar(
                x=[entry["date"] for entry in data],
                y=[entry["wind_speed"] for entry in data],
                name="Скорость ветра (км/ч)",
                marker=dict(color="lightblue"),
            ),
            go.Bar(
                x=[entry["date"] for entry in data],
                y=[entry["humidity"] for entry in data],
                name="Влажность (%)",
                marker=dict(color="lightgreen"),
            ),
        ],
        "layout": go.Layout(
            title="Скорость ветра и влажность",
            xaxis={"title": "Дата"},
            yaxis={"title": "Значение"},
            barmode="group",
        ),
    }

    precipitation_fig = {
        "data": [
            go.Bar(
                x=[entry["date"] for entry in data],
                y=[entry["precipitation_probability"] for entry in data],
                name="Вероятность осадков (%)",
                marker=dict(color="lightcoral"),
            )
        ],
        "layout": go.Layout(
            title="Вероятность осадков",
            xaxis={"title": "Дата"},
            yaxis={"title": "Вероятность (%)"},
        ),
    }

    return temperature_fig, wind_humidity_fig, precipitation_fig


def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/dummypath/")

    app.layout = html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.H1("Прогноз погоды на 5 дней"),
            dcc.Graph(id="temperature-graph"),
            dcc.Graph(id="wind-humidity-graph"),
            dcc.Graph(id="precipitation-graph"),
        ]
    )

    @app.callback(
        [
            Output("temperature-graph", "figure"),
            Output("wind-humidity-graph", "figure"),
            Output("precipitation-graph", "figure"),
        ],
        [Input("url", "search")],
    )
    def update_layout(search):
        parsed_url = urlparse(search)
        params = parse_qs(parsed_url.query)
        location_key = params.get("location_key")[0]
        days = params.get("days", 1)[0]

        if not location_key or not days.isdigit():
            server.logger.error(f"no location key or days: {location_key=}, {days=}")
            return {}, {}, {}

        days = int(days)

        try:
            forecast_res = asyncio.run(get_forecast(location_key, days))
        except (ConnectionError, TimeoutError) as e:
            server.logger.error(f"Connection timeout")
            return {}, {}, {}
        except aiohttp.ClientResponseError as e:
            server.logger.error(f"Response error: {e.status}")
            return {}, {}, {}

        if not forecast_res:
            server.logger.error(f"None forecast_res: {forecast_res=}")
            return {}, {}, {}

        forecasts = [
            parse_forecast(day_forecast)
            for day_forecast in forecast_res["DailyForecasts"]
        ]

        server.logger.info(f"parsed forecasts {forecasts}")

        return create_figs(forecasts)

    return app
