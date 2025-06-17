from aiogram import Router, F, types
from db.repository import get_routes_by_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
"""
Роутер для отображения всех сохранённых маршрутов пользователя через команду /routes.
"""

@router.message(F.text == "/routes")
async def show_routes(message: types.Message):
    """
    Обработчик команды `/routes`.

    Извлекает список маршрутов пользователя из базы данных и отображает их
    в виде inline-кнопок. Если маршрутов нет — уведомляет пользователя.

    Args:
        message (types.Message): Объект сообщения от Telegram-пользователя.
    """
    routes = await get_routes_by_user(message.from_user.id)
    if not routes:
        await message.answer("У тебя ещё нет сохранённых маршрутов.")
        return

    buttons = []
    for route in routes:
        btn_text = f"{route.route_name or 'Без имени'}: {route.city_from} → {route.city_to}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"route_select:{route.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Выбери маршрут:", reply_markup=keyboard)
