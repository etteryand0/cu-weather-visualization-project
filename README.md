# Проект AccuWeather. Красный питон 12 неделя

> Выполнил Сергин Сергей

Веб-сервис, который предсказывает вероятность плохой погоды для заданного маршрута, используя данные AccuWeather API. Сервис предоставляет пользователю удобные визуализации и прогнозы погоды для разных точек маршрута и временных интервалов.

## Запуск проекта

1. Установить зависимости 
```shell
pip install -e .
```
2. Записать API ключ в .env файл по аналогии с .env.example
```shell
echo "ACCUWEATHER_API_KEY=myaccuweathertoken" > .env
```
3. Запустить веб приложение
```shell
python -m flask --app cu_weather_viz_app run --debug
```

## Тестирование

Что бы проверить функцию `check_weather_bad`, запустите юнит тесты 
```shell
python -m unittest discover
```

## Обработанные ошибки

1. **ConnectionError**
   - **Описание**: Эта ошибка возникает, когда не удаётся подключиться к серверу API. Это может случиться из-за проблем с интернетом или если сервер недоступен
   - **Обработка**: Если возникает эта ошибка, мы записываем её в лог и показываем пользователю сообщение о том, что сервис погоды сейчас недоступен.
   - **Влияние на систему**: Если соединение не удалось, мы не можем получить данные о погоде. Пользователь не получает актуальную информацию, но приложение продолжает работать и сообщает о проблеме.

2. **TimeoutError**
   - **Описание**: Эта ошибка возникает, когда запрос к API занимает слишком много времени. Это может произойти, если сервер отвечает слишком медленно.
   - **Обработка**: Аналогично `ConnectionError`, мы записываем ошибку в лог и показываем пользователю сообщение о недоступности сервиса.
   - **Влияние на систему**: Как и в первом случае, мы не можем получить данные о погоде, но приложение продолжает работать и уведомляет пользователя о проблеме.
3. **requests.exceptions.HTTPError**
   - **Описание**: Эта ошибка возникает, когда сервис AccuWeather API возвращает код ошибки HTTP.
   - **Обработка**: Если возникает эта ошибка, мы записываем её в лог и показываем пользователю сообщение, основанное на коде ошибки, полученном от сервера. Уникально обрабатываются статусы 400, 401, 403, все остальные ошибки возвращают типичную ошибку недоступности сервиса.
   - **Влияние на систему**: Запрос к API выполнен, но сервер вернул ошибку, что может означать, что что-то не так с запрашиваемыми данными (например, неверный ключ местоположения или превышенный лимит запросов). Пользователь получает информацию о проблеме и может проверить введённые данные.

