# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions.

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to Run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```bash
cd bot && python main.py
```

## Required Secrets

Set these in Replit Secrets (already configured):

| Secret      | Description                         |
|-------------|-------------------------------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather  |
| `ADMIN_ID`  | Telegram numeric user ID            |
| `MONGO_URI` | MongoDB connection string           |

## Install Dependencies

```bash
cd bot && pip install -r requirements.txt
```

## Project Structure

```
bot/
├── handlers/          # Telegram update handlers
├── keyboards/         # Inline keyboards
├── filters/           # Admin-only filter
├── services/          # Business logic (subscriptions, auto-renewals)
├── database/          # MongoDB connection & models
├── utils/             # Utility functions
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## Admin Commands

| Command      | Description                            |
|--------------|----------------------------------------|
| `/admin`     | Open the admin panel                   |
| `/addplan`   | Add a new subscription plan            |
| `/topup`     | Top up a user's wallet balance         |

## User Preferences

- Keep the existing project structure and stack
