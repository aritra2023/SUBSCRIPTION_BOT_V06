# Flix Verse Premium Bot

A production-grade Telegram bot for managing Flix Verse premium subscriptions, built with Python + aiogram 3 + MongoDB.

## How to run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```
cd bot && python main.py
```

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## Required secrets

Set these in Replit Secrets before starting:

| Secret      | Description                              |
|-------------|------------------------------------------|
| `BOT_TOKEN` | Telegram bot token (from BotFather)      |
| `ADMIN_ID`  | Your Telegram numeric user ID            |
| `MONGO_URI` | MongoDB connection string (e.g. Atlas)   |

## Project structure

```
bot/
├── handlers/        # Telegram update handlers (start, subscription, wallet, history, admin)
├── keyboards/       # Inline keyboards
├── filters/         # Admin-only filter
├── services/        # Business logic (subscriptions, telegraph)
├── database/        # MongoDB connection & models
├── utils/           # Helper functions
├── config.py        # Loads env vars
├── loader.py        # Bot, Dispatcher, Motor client instances
└── main.py          # Entry point — polling + auto-renew loop
```

## Admin commands

| Command      | Description                        |
|--------------|------------------------------------|
| `/admin`     | Open the admin panel               |
| `/addplan`   | Add a new subscription plan        |
| `/topup`     | Top up a user's wallet balance     |

## User preferences

- Keep the existing `bot/` directory structure — do not restructure or migrate.
