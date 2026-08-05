# Flix Verse Premium Bot

A production-grade Telegram bot for managing Flix Verse premium subscriptions.

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

| Secret      | Description                              |
|-------------|------------------------------------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather       |
| `ADMIN_ID`  | Your Telegram numeric user ID            |
| `MONGO_URI` | MongoDB connection string (e.g. Atlas)   |

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
├── utils/
│   └── helpers.py     # Utility functions
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## Admin Commands

| Command      | Description                              |
|--------------|------------------------------------------|
| `/admin`     | Open the admin panel                     |
| `/addplan`   | Add a new subscription plan              |
| `/topup`     | Top up a user's wallet balance           |
| `/penalty`   | Deduct penalty from a user's wallet      |

## Admin Panel Features

- **📊 Stats** — Total users and active plans
- **👥 All Users** — List all registered users
- **📢 Broadcast** — Send a message to all users
- **🖼 Set Banner** — Upload the /start banner image
- **📦 Manage Plans** — View and add subscription plans

## User Preferences
