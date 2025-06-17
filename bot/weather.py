import aiohttp
import logging
import os
from dotenv import load_dotenv

# Загрузка API ключей из переменных окружения
load_dotenv()
GEOCODIK_API_KEY = os.getenv("GEOCODIK_API_KEY")
YANDEX_WEATHER_API_KEY = os.getenv("YANDEX_WEATHER_API_KEY")
"""
API-ключи для доступа к сервисам Яндекс Геокодера и Яндекс Погоды.

- `GEOCODIK_API_KEY`: ключ для получения координат по названию города.
- `YANDEX_WEATHER_API_KEY`: ключ для получения погодных данных по координатам.
"""

condition_map = {
    "clear": "ясно",
    "partly-cloudy": "малооблачно",
    "cloudy": "облачно с прояснениями",
    "overcast": "пасмурно",
    "drizzle": "морось",
    "light-rain": "небольшой дождь",
    "rain": "дождь",
    "moderate-rain": "умеренно сильный дождь",
    "heavy-rain": "сильный дождь",
    "continuous-heavy-rain": "длительный сильный дождь",
    "showers": "ливень",
    "wet-snow": "дождь со снегом",
    "light-snow": "небольшой снег",
    "snow": "снег",
    "snow-showers": "снегопад",
    "hail": "град",
    "thunderstorm": "гроза",
    "thunderstorm-with-rain": "дождь с грозой",
    "thunderstorm-with-hail": "гроза с градом",
}
"""
Словарь соответствий погодных условий (из API Яндекса) и их перевода на русский язык.
Используется для отображения понятного состояния погоды пользователю.
"""

wind_dir_map = {
    'nw': 'северо-западный',
    'n': 'северный',
    'ne': 'северо-восточный',
    'e': 'восточный',
    'se': 'юго-восточный',
    's': 'южный',
    'sw': 'юго-западный',
    'w': 'западный',
    'c': 'штиль'  # calm
}
"""
Словарь соответствий кодов направлений ветра (из API Яндекса) и их перевода на русский язык.
"""
def deg_to_wind_dir(deg: int) -> str:
    """
    Преобразует направление ветра в градусах в текстовое обозначение на русском языке.
        Args:
        deg (int): Направление ветра в градусах (0–360). 
        Returns:
        str: Направление ветра словами (например, "северный", "юго-восточный").
    """
    dirs = ['северный', 'северо-восточный', 'восточный', 'юго-восточный',
            'южный', 'юго-западный', 'западный', 'северо-западный']
    ix = round(deg / 45) % 8
    return dirs[ix]


async def get_coords(city: str):
    """
    Получает координаты города по его названию с помощью Яндекс Геокодера.

    Args:
        city (str): Название города, для которого необходимо определить координаты.

    Returns:
        tuple[float, float] | None: Кортеж (широта, долгота) или None при ошибке запроса.
    """
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": GEOCODIK_API_KEY,
        "geocode": city,
        "format": "json",
        "lang": "ru_RU"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка при геокодинге города {city}: {resp.status}")
                return None
            data = await resp.json()
            try:
                pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, pos.split())
                return lat, lon
            except (IndexError, KeyError):
                logging.error(f"Не удалось получить координаты для города {city}")
                return None

async def get_weather(lat: float, lon: float):
    """
    Получает погодные данные по координатам с помощью API Яндекс Погоды.

    Args:
        lat (float): Широта города.
        lon (float): Долгота города.

    Returns:
        dict | None: Словарь с погодными данными или None в случае ошибки.
    """
    """Метод проверки API погоды"""
    url = "https://api.weather.yandex.ru/v2/forecast"
    headers = {"X-Yandex-API-Key": YANDEX_WEATHER_API_KEY}
    params = {
        "lat": lat,
        "lon": lon,
        "lang": "ru_RU",
        "limit": 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка при получении погоды: {resp.status}")
                return None
            return await resp.json()

async def get_weather_by_city(city: str):
    coords = await get_coords(city)
    if coords is None:
        return None
    lat, lon = coords
    return await get_weather(lat, lon)
