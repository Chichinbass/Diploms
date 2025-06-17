# bot/handlers/routeweather.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db.repository import get_routes_by_user
from bot.weather import get_weather_by_city, condition_map, wind_dir_map as wind_directions


router = Router()
"""
Роутер для обработки команды /routeweather — отображения прогноза погоды для сохранённых маршрутов пользователя.
"""

@router.message(F.text == "/routeweather")
async def show_user_routes(message: Message):
    """
    Обработчик команды `/routeweather`.

    Отправляет пользователю список его маршрутов в виде inline-кнопок для выбора.
    По нажатию пользователь получает прогноз погоды по каждому городу в маршруте.

    Args:
        message (Message): Сообщение Telegram от пользователя.
    """
    routes = await get_routes_by_user(message.from_user.id)
    if not routes:
        await message.answer("📭 У тебя пока нет сохранённых маршрутов.")
        return

    buttons = [
        [InlineKeyboardButton(text=route.route_name or f"{route.city_from} - {route.city_to}",
                              callback_data=f"rw_{route.id}")]
        for route in routes
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("🗺 Выбери маршрут для прогноза погоды:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rw_"))
async def send_route_weather(callback: CallbackQuery):
    """
    Обработчик callback-запроса на просмотр погоды по маршруту.

    Получает ID маршрута из callback_data, запрашивает погоду для двух городов
    и отправляет результат в сообщении.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя Telegram.
    """
    route_id = int(callback.data.split("_")[1])
    routes = await get_routes_by_user(callback.from_user.id)
    route = next((r for r in routes if r.id == route_id), None)

    if not route:
        await callback.message.edit_text("❌ Маршрут не найден.")
        return

    weather_from = await get_weather_by_city(route.city_from)
    weather_to = await get_weather_by_city(route.city_to)

    def format_weather(city: str, weather: dict) -> str:
        """
        Форматирует погодные данные для вывода в Telegram.

        Args:
            city (str): Название города.
            weather (dict): Ответ API с погодой.

        Returns:
            str: Строка с информацией о погоде.
        """
        if not weather:
            return f"⚠️ Нет данных для {city}\n"

        fact = weather.get("fact", {})
        condition_code = fact.get("condition", "нет данных")
        condition_rus = condition_map.get(condition_code, condition_code)

        wind_dir_code = fact.get("wind_dir", "нет данных")
        wind_dir = wind_directions.get(wind_dir_code, wind_dir_code)

        return (
            f"📍 {city}:\n"
            f"🌡 Темп: {fact.get('temp', 'н/д')}°C, ощущается как {fact.get('feels_like', 'н/д')}°C\n"
            f"💨 Ветер: {fact.get('wind_speed', 'н/д')} м/с, {wind_dir}\n"
            f"🔍 Состояние: {condition_rus}\n"
        )

    text = f"📦 Погода по маршруту «{route.route_name or f'{route.city_from} - {route.city_to}'}»:\n\n"
    text += format_weather(route.city_from, weather_from)
    text += "\n"
    text += format_weather(route.city_to, weather_to)

    await callback.message.edit_text(text)
