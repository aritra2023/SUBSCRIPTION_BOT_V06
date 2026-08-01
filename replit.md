# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions.

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to run

The bot lives in the `bot/` directory. The workflow `Flix Verse Telegram Bot` runs it:

```bash
cd bot && python main.py
```

Dependencies are installed via:

```bash
cd bot && pip install -r requirements.txt
```

## Required secrets

Set these in Replit Secrets (all three are required):

| Secret      | Description                         |
|-------------|-------------------------------------|
| `BOT_TOKEN` | Telegram bot token (from BotFather) |
| `ADMIN_ID`  | Your numeric Telegram user ID       |
| `MONGO_URI` | MongoDB connection string           |

## Project structure

```
bot/
├── handlers/          # Telegram update handlers
│   ├── start.py       # /start command & main menu
│   ├── subscription.py # Buy, view plan, help, support
│   ├── wallet.py      # Wallet balance
│   ├── history.py     # Transaction history
│   └── admin.py       # Admin panel
├── keyboards/
│   └── inline.py      # All inline keyboards
├── filters/
│   └── admin.py       # Admin-only filter
├── services/
│   └── subscription.py # Business logic layer
├── database/
│   ├── db.py          # MongoDB connection & indexes
│   └── models.py      # TypedDict models
├── utils/
│   └── helpers.py     # Utility functions
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## Admin commands

| Command      | Description                        |
|--------------|------------------------------------|
| `/admin`     | Open the admin panel               |
| `/addplan`   | Add a new subscription plan        |
| `/topup`     | Top up a user's wallet balance     |

## User preferences
