# Flix Verse Premium Bot

A production-grade Telegram bot for managing Flix Verse premium subscriptions.

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to Run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```
cd bot && python main.py
```

## Required Secrets / Environment Variables

| Key | Type | Description |
|---|---|---|
| `BOT_TOKEN` | Secret | Telegram bot token from BotFather |
| `MONGO_URI` | Secret | MongoDB connection string |
| `ADMIN_ID` | Env var (shared) | Your Telegram numeric user ID |

## Project Structure

```
bot/
├── handlers/          # Telegram update handlers
├── keyboards/         # Inline keyboards
├── filters/           # Admin-only filter
├── services/          # Business logic (subscriptions, auto-renewals)
├── database/          # MongoDB connection & models
├── utils/             # Helper functions
├── config.py          # Loads env vars
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## Admin Commands

| Command | Description |
|---|---|
| `/admin` | Open the admin panel |
| `/addplan` | Add a new subscription plan |
| `/topup` | Top up a user's wallet balance |

## User preferences
