from aiogram import Router, F
from aiogram.types import Message
from bot.weather import get_weather_by_city, condition_map, wind_dir_map, deg_to_wind_dir

router = Router()
"""
Роутер `aiogram`, который объединяет все обработчики команд, используемых в Telegram-боте.
"""
# Команда /start
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    """
    Обработчик команды `/start`.

    Отправляет приветственное сообщение пользователю при первом запуске бота.

    Args:
        message (Message): Сообщение Telegram от пользователя.
    """
    await message.answer(
        "👋 Привет! Я бот помощник планированя туристических маршрутов.\n"
        "Напиши /help чтобы узнать, что я умею!"
    )

# Команда /help
@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """
    Обработчик команды `/help`.

    Возвращает список всех доступных команд и их описания в формате справки.

    Args:
        message (Message): Сообщение Telegram от пользователя.
    """
    text = (
        "📖 <b>Доступные команды:</b>\n\n"
        "☀️ <b>/weather &lt;город&gt;</b> — показать погоду в городе\n"
        "📦 <b>/newroute &lt;город_откуда&gt; - &lt;город_куда&gt;</b> ; Название маршрута\n"
        "📋 <b>/routes</b> — посмотреть все маршруты\n"
        "🌦 <b>/routeweather</b> — погода по маршрутам\n"
        "🗑 <b>/deleteroute</b> — удалить маршрут\n"
        "ℹ️ <b>/help</b> — справка по командам"
    )
    await message.answer(text, parse_mode="HTML")

# Команда /weather
@router.message(F.text.startswith('/weather'))
async def cmd_weather(message: Message):
    city = message.text.replace('/weather', '').strip()
    if not city:
        await message.answer("❗ Укажи город, например: <b>/weather Москва</b>", parse_mode="HTML")
        return

    weather = await get_weather_by_city(city)
    if not weather:
        await message.answer(f"⚠️ Не удалось получить данные для города <b>{city}</b>", parse_mode="HTML")
        return

    fact = weather.get("fact", {})
    condition_code = fact.get("condition", "нет данных")
    condition_rus = condition_map.get(condition_code, condition_code)

    wind_speed = fact.get("wind_speed", "нет данных")
    wind_dir_code = fact.get("wind_dir")
    wind_deg = fact.get("wind_deg")

    if wind_dir_code in wind_dir_map:
        wind_dir_rus = wind_dir_map[wind_dir_code]
    elif isinstance(wind_deg, int):
        wind_dir_rus = deg_to_wind_dir(wind_deg)
    else:
        wind_dir_rus = "нет данных"

    text = (
        f"📍 <b>Погода в городе {city}:</b>\n"
        f"🌡 Температура: <b>{fact.get('temp', 'нет данных')}°C</b>\n"
        f"🤗 Ощущается как: <b>{fact.get('feels_like', 'нет данных')}°C</b>\n"
        f"💨 Ветер: <b>{wind_speed} м/с</b>, направление: <b>{wind_dir_rus}</b>\n"
        f"🔍 Состояние: <b>{condition_rus}</b>"
    )
    await message.answer(text, parse_mode="HTML")
