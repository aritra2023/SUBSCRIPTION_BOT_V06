# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions.

## Features

- 🎬 Premium subscription management
- 💎 Multiple plan tiers
- 💰 Wallet system with balance tracking
- 📋 Transaction history
- 📢 Admin broadcast to all users
- 🖼 Customisable banner image
- ⚙️ Full admin panel

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
├── utils/
│   └── helpers.py     # Utility functions
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable    | Description                         |
|-------------|-------------------------------------|
| `BOT_TOKEN` | Your Telegram bot token (BotFather) |
| `ADMIN_ID`  | Your Telegram numeric user ID       |
| `MONGO_URI` | MongoDB connection string           |

## Installation

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python main.py
```

## Admin Commands

| Command      | Description                            |
|--------------|----------------------------------------|
| `/admin`     | Open the admin panel                   |
| `/addplan`   | Add a new subscription plan            |
| `/topup`     | Top up a user's wallet balance         |

## Admin Panel Actions

- **📊 Stats** — Total users and active plans
- **👥 All Users** — List all registered users
- **📢 Broadcast** — Send message to all users
- **🖼 Set Banner** — Upload the /start banner image
- **📦 Manage Plans** — View and add subscription plans

## License

MIT
