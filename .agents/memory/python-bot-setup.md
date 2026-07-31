---
name: Python bot setup
description: How Python is installed and the Telegram bot runs in this workspace
---

Python 3.11 is installed via the `installProgrammingLanguage` module. Packages (aiogram, motor, python-dotenv) installed via `installLanguagePackages`. The bot runs via a console workflow named "Flix Verse Telegram Bot" with command `cd bot && python main.py`.

**Why:** pnpm monorepo template doesn't include Python by default; it must be installed as a module before pip packages work.

**How to apply:** Any future Python package installs use `installLanguagePackages({ language: "python", packages: [...] })`. Restart the "Flix Verse Telegram Bot" workflow after code changes.
