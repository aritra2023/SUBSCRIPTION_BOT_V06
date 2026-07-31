# Flix Verse Premium Bot

A production-grade Telegram subscription bot for **Flix Verse** premium channels, built with Python + aiogram 3.x.

## Run & Operate

- **Bot workflow:** `cd bot && python main.py` (configured as "Flix Verse Telegram Bot")
- **Bot username:** @PremiumVerse_Robot
- **Restart bot:** Use the "Flix Verse Telegram Bot" workflow

## Stack

- Python 3.11
- aiogram 3.x (async Telegram bot framework)
- Motor 3.x (async MongoDB driver)
- python-dotenv (environment config)
- MongoDB (database)

## Required Secrets

| Secret | Description |
|--------|-------------|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `ADMIN_ID` | Admin's Telegram numeric user ID |
| `MONGO_URI` | MongoDB Atlas connection string |

## Where Things Live

```
bot/
├── handlers/       # Telegram handlers (start, subscription, wallet, history, admin)
├── keyboards/      # Inline keyboards
├── middlewares/    # DB injection middleware
├── filters/        # Admin-only filter
├── services/       # Business logic (users, plans, subscriptions, wallet)
├── database/       # MongoDB connection & models
├── utils/          # Helper functions
├── config.py       # Loads env vars
├── loader.py       # Bot + Dispatcher instances
└── main.py         # Entry point
```

## Admin Commands

- `/admin` — Admin panel (stats, users, broadcast, set banner, manage plans)
- `/addplan` — Add a new subscription plan (format: `name|Display Name|price|days|description`)
- `/topup` — Top up a user's wallet balance

## User Features

- `/start` — Welcome message with banner image + main menu
- **BUY SUBSCRIPTION** — Browse and purchase plans
- **VIEW PLAN** — Check active subscription
- **HELP** — Bot usage guide
- **HISTORY** — Transaction history
- **SUPPORT** — Contact admin
- **YOUR WALLET** — View wallet balance

## First-Time Setup

1. Start the bot with `/start`
2. Set the banner image: `/admin` → 🖼 SET BANNER → send the anime image
3. Use `/topup` to add balance to users' wallets before they can purchase

## User Preferences

- Python only (aiogram 3.x, no Node.js)
- Exact UI clone from provided screenshot (blockquote formatting, exact button layout)
- Modular structure following professional Telegram bot conventions

## Gotchas

- After adding new plans, they appear immediately in the bot
- Banner image is stored as a Telegram `file_id` in MongoDB (settings collection)
- Wallet top-up is admin-only; users purchase with wallet balance
