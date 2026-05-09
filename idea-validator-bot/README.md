# 🧠 Валидатор идей — Telegram Bot

Telegram бот для быстрой валидации гипотез через аргументы ЗА и ПРОТИВ.

## 🚀 Быстрый старт

1. **Получи токен бота** у [@BotFather](https://t.me/BotFather)
2. **Скопируй `.env.example` → `.env`** и вставь токен:
   ```
   BOT_TOKEN=123456:ABC-DEF...
   ```
3. **Установи зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Запусти бота:**
   ```bash
   python -m bot.main
   ```

## 📦 Docker

```bash
docker-compose up -d
```

## 📱 Telegram Mini App

Для использования WebApp:
1. Захости папку `webapp/` на любом HTTPS-сервере
2. Укажи URL в `.env`: `WEBAPP_URL=https://your-domain.com/webapp/`
3. Настрой WebApp URL через [@BotFather](https://t.me/BotFather) → Menu Button

## 📂 Структура

```
bot/
├── main.py              # Точка входа
├── config.py            # Настройки
├── states.py            # FSM состояния
├── handlers/            # Обработчики
│   ├── commands.py      # /start, /help
│   ├── idea.py          # Создание идеи
│   ├── arguments.py     # Аргументы ЗА/ПРОТИВ
│   ├── history.py       # История идей
│   └── export.py        # Экспорт TXT/JSON
├── keyboards/           # Клавиатуры
│   ├── inline.py        # Inline кнопки
│   └── reply.py         # Reply клавиатура
├── services/            # Бизнес-логика
│   ├── validator.py     # Логика валидации
│   ├── database.py      # SQLite/PostgreSQL
│   └── export.py        # Генерация файлов
└── utils/
    └── formatting.py    # Форматирование
webapp/                  # Telegram Mini App
```

## 🧠 Логика валидации

Вес аргументов: слабый=1, средний=2, сильный=3

- `total < 3` → 🤔 Нужно больше данных
- `pro_weighted > con_weighted × 1.5` → 🚀 Идея перспективная
- `con_weighted > pro_weighted × 1.5` → ❌ Идея слабая
- иначе → ⚖️ промежуточная оценка

## 🛠 Технологии

- [aiogram 3.x](https://docs.aiogram.dev/) — асинхронный бот
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) — ORM
- [SQLite](https://www.sqlite.org/) — база данных (dev)
- [PostgreSQL](https://www.postgresql.org/) — база данных (prod)
