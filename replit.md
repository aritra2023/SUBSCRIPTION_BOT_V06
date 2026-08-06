# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions, built with Python/aiogram and MongoDB.

## How to run

The bot is configured as the **"Flix Verse Telegram Bot"** workflow, which runs:

```
cd bot && python main.py
```

Dependencies are installed via pip from `bot/requirements.txt`.

## Required secrets

Set these in Replit Secrets before starting the bot:

| Secret      | Description                              |
|-------------|------------------------------------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather       |
| `ADMIN_ID`  | Your Telegram numeric user ID            |
| `MONGO_URI` | MongoDB connection string (e.g. Atlas)   |

## Stack

- **Python 3.11** — runtime
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## Project structure

```
bot/
├── handlers/       # Telegram update handlers (start, subscription, wallet, history, admin)
├── keyboards/      # Inline keyboard definitions
├── filters/        # Admin-only filter
├── services/       # Business logic (subscription, telegraph)
├── database/       # MongoDB connection & models
├── utils/          # Helper utilities
├── config.py       # Reads secrets from environment
├── loader.py       # Bot & dispatcher instances
└── main.py         # Entry point
```

## Admin commands

| Command      | Description                        |
|--------------|------------------------------------|
| `/admin`     | Open the admin panel               |
| `/addplan`   | Add a new subscription plan        |
| `/topup`     | Top up a user's wallet balance     |
| `/penalty`   | Deduct penalty from a user wallet  |

## User preferences
