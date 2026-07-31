# Flix Verse Premium Bot

A production-grade Telegram bot for managing **Flix Verse** premium subscriptions.

## Stack

- **Python 3.11**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to Run

The bot runs via the **"Flix Verse Telegram Bot"** workflow:

```
cd bot && python main.py
```

## Required Secrets

Set in Replit Secrets (already configured):

| Secret      | Description                              |
|-------------|------------------------------------------|
| `BOT_TOKEN` | Telegram bot token from BotFather        |
| `ADMIN_ID`  | Your Telegram numeric user ID            |
| `MONGO_URI` | MongoDB connection string (e.g. Atlas)   |

## Features

- 🎬 Premium subscription management
- 💎 Multiple plan tiers
- 💰 Wallet system with balance tracking
- 📋 Transaction history
- 📢 Admin broadcast to all users
- 🖼 Customisable banner image
- ⚙️ Full admin panel

## Admin Commands

| Command      | Description                            |
|--------------|----------------------------------------|
| `/admin`     | Open the admin panel                   |
| `/addplan`   | Add a new subscription plan            |
| `/topup`     | Top up a user's wallet balance         |

## Project Structure

```
bot/
├── handlers/          # Telegram update handlers
├── keyboards/         # Inline keyboards
├── middlewares/       # Database injection middleware
├── filters/           # Admin-only filter
├── services/          # Business logic layer
├── database/          # MongoDB connection & models
├── utils/             # Utility functions
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point
```

## User Preferences

<!-- Add preferences here as needed -->
