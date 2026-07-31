---
name: Python bot setup
description: Durable operational notes for the Flix Verse Telegram bot on Replit
---

Packages must be installed via `installLanguagePackages({ language: "python", ... })` — direct pip calls fail due to Nix store permissions. The `.pythonlibs` directory is already on `sys.path` so user-installed packages are picked up automatically.

**Why:** The Nix store is read-only; pip with `--target` or without `PYTHONUSERBASE` override fails silently or errors. Only the Replit package manager callback writes to the correct user site-packages path.

**How to apply:** Any future Python dependency changes should use `installLanguagePackages`. Node version must stay at nodejs-24 (or newer) to satisfy the pnpm workspace lockfile — do not downgrade it when adding Python support.
