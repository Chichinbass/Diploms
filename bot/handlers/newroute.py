from aiogram import Router, F, types
from db.repository import save_route, get_routes_by_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
"""
Роутер для обработки команды /newroute — сохранения маршрутов между городами.
"""
@router.message(F.text.startswith("/newroute"))
async def handle_newroute(message: types.Message):
    """
    Обработчик команды `/newroute`.

    Команда позволяет сохранить туристический маршрут между двумя городами.
    Пользователь может указать имя маршрута опционально после `;`.

    Пример:
        `/newroute Москва - Санкт-Петербург; Поездка на выходные`

    Поддерживаемый формат:
        `/newroute <город_откуда> - <город_куда> [; имя_маршрута]`

    Args:
        message (types.Message): Сообщение Telegram от пользователя.
    """
    text = message.text.removeprefix("/newroute").strip()

    # Ожидается формат: /newroute <город1> - <город2> [; имя маршрута]
    # Например: /newroute Москва - Санкт-Петербург; Мой маршрут
    route_name = None
    if ";" in text:
        route_part, route_name = map(str.strip, text.split(";", 1))
    else:
        route_part = text

    if "-" not in route_part:
        await message.answer("❌ Используй формат: /newroute <город1> - <город2> [; имя маршрута]")
        return

    try:
        city_from, city_to = map(str.strip, route_part.split("-", 1))
    except Exception:
        await message.answer("❌ Не удалось разобрать маршрут.")
        return

    try:
        await save_route(
            telegram_id=message.from_user.id,
            city_from=city_from,
            city_to=city_to,
            route_name=route_name
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении маршрута: {e}")
        return

    name_text = f" с именем '{route_name}'" if route_name else ""
    await message.answer(f"✅ Маршрут сохранён: {city_from} → {city_to}{name_text}")

