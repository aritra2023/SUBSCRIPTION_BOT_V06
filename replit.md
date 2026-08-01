# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions, built with Python + aiogram 3.x and MongoDB.

## How to Run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```
cd bot && python main.py
```

## Required Secrets

Set these in Replit Secrets before starting:

| Secret      | Description                                      |
|-------------|--------------------------------------------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather               |
| `ADMIN_ID`  | Your Telegram numeric user ID                    |
| `MONGO_URI` | MongoDB connection string (Atlas or self-hosted) |

## Installing Dependencies

```bash
cd bot && pip install -r requirements.txt
```

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## Project Structure

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
├── middlewares/
│   └── db.py          # Database injection middleware
├── filters/
│   └── admin.py       # Admin-only filter
├── services/
│   └── subscription.py # Business logic layer
├── database/
│   ├── db.py          # MongoDB connection & indexes
│   └── models.py      # TypedDict models
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

<!-- Add any user-specific preferences here -->
