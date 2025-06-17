from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db.repository import get_routes_by_user, delete_route  # Импорт из слоя работы с БД

router = Router()
"""
Роутер для обработки команд, связанных с удалением маршрутов пользователя.
"""
@router.message(F.text == "/deleteroute")
async def cmd_delete_route(message: Message):
    """
    Обработчик команды `/deleteroute`.

    Получает список сохранённых маршрутов пользователя и предлагает выбрать один
    из них для удаления через интерфейс inline-кнопок.

    Args:
        message (Message): Объект сообщения Telegram от пользователя.
    """
    routes = await get_routes_by_user(message.from_user.id)
    if not routes:
        await message.answer("📭 У вас пока нет сохранённых маршрутов.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=route.route_name or f"{route.city_from} - {route.city_to}", callback_data=f"del_{route.id}")
        ] for route in routes]
    )
    await message.answer("🗑 Выберите маршрут для удаления:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("del_"))
async def process_delete_route(callback: CallbackQuery):
    """
    Обработчик callback-запроса от inline-кнопок удаления маршрута.

    Извлекает ID маршрута из callback-данных и удаляет его из базы данных.

    Args:
        callback (CallbackQuery): Объект callback-запроса Telegram от пользователя.
    """
    route_id = int(callback.data.split("_")[1])
    await delete_route(route_id)  # Удаляем маршрут из БД
    await callback.message.edit_text("✅ Маршрут удалён.")
