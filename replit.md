# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions.

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```
cd bot && python main.py
```

## Required secrets

Set these in Replit Secrets (already configured):

| Secret      | Description                                      |
|-------------|--------------------------------------------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather               |
| `ADMIN_ID`  | Your numeric Telegram user ID                    |
| `MONGO_URI` | MongoDB connection string (e.g. Atlas URI)       |

## Project structure

```
bot/
├── handlers/         # Telegram update handlers (start, subscription, wallet, history, admin)
├── keyboards/        # Inline keyboards
├── filters/          # Admin-only filter
├── services/         # Business logic (subscriptions, Telegraph)
├── database/         # MongoDB connection & models
├── utils/            # Helper utilities
├── config.py         # Loads env vars
├── loader.py         # Bot & dispatcher instances
└── main.py           # Entry point
```

## Admin commands

| Command      | Description                         |
|--------------|-------------------------------------|
| `/admin`     | Open the admin panel                |
| `/addplan`   | Add a new subscription plan         |
| `/topup`     | Top up a user's wallet balance      |

## Dependencies

Install with:

```bash
cd bot && pip install -r requirements.txt
```

## User preferences

<!-- Add any user-specific preferences here -->
