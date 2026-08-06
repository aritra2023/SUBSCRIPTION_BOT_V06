# Flix Verse Premium Bot

A production-grade Telegram bot for managing Flix Verse premium subscriptions.

## Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot framework
- **Motor** — async MongoDB driver
- **python-dotenv** — environment variable loading

## How to Run

```bash
cd bot && python main.py
```

The workflow **Flix Verse Telegram Bot** runs this automatically.

## Required Secrets

| Secret | Description |
|--------|-------------|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `ADMIN_ID` | Telegram numeric user ID of the admin |
| `MONGO_URI` | MongoDB connection string (e.g. `mongodb+srv://...`) |

## Project Structure

```
bot/
├── handlers/          # Telegram update handlers
│   ├── start.py       # /start command & main menu
│   ├── subscription.py # Buy, view plans, help, support
│   ├── wallet.py      # Wallet balance & auto-renew toggle
│   ├── history.py     # Transaction history (Telegraph page)
│   └── admin.py       # Admin panel
├── keyboards/
│   └── inline.py      # All inline keyboards
├── services/
│   ├── subscription.py # Business logic (users, plans, wallet)
│   └── telegraph.py   # Telegraph history page generation
├── database/
│   ├── db.py          # MongoDB connection & indexes
│   └── models.py      # TypedDict models
├── utils/
│   └── helpers.py     # Shared utilities (text formatting, welcome text)
├── filters/
│   └── admin.py       # Admin-only filter
├── config.py          # Environment config
├── loader.py          # Bot & dispatcher instances
└── main.py            # Entry point + auto-renew loop
```

## Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Open the admin panel |
| `/addplan` | Add a new subscription plan |
| `/topup` | Top up a user's wallet |
| `/penalty` | Deduct a penalty from a user's wallet |

## User preferences

- Keep existing Python/aiogram/Motor stack — do not migrate or restructure
- Minimal changes only; no unnecessary files or packages
