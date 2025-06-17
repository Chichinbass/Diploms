travel_weather_bot/
├── bot/                        # Логика Telegram-бота
│   ├── __init__.py
│   ├── handlers/              # Команды и обработчики
│   │   ├── __init__.py
│   │   └── basic.py           # /start, /weather и т.д.
│   └── weather.py             # Работа с API Яндекс.Погоды
│
├── config/
│   └── config.py              # Загрузка токенов и API-ключей
│
├── main.py                    # Точка входа: инициализация и запуск
├── requirements.txt
├── .env