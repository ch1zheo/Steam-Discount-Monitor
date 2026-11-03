# Contributing

Thanks for wanting to help! This project is small, so a few simple rules are enough.

## Reporting a bug

Open an [issue](../../issues) and include:

- what you expected and what actually happened;
- the console output around the error (with the bot token and chat ID removed);
- your OS and Python version (`python --version`).

## Suggesting a feature

Open an issue and describe the problem you want to solve, not only the solution. Features that keep the bot small and dependency-free are preferred.

## Pull requests

1. Fork the repository and create a branch from `main`:
   ```bash
   git checkout -b fix/steam-selectors
   ```
2. Keep the change focused: one fix or one feature per pull request.
3. Match the existing style: small modules, type hints where the code already uses them, no new dependencies without a good reason.
4. User-facing text (console logs and Telegram messages) is in Russian — keep it that way so the bot stays consistent.
5. Test manually before opening a pull request:
   ```bash
   cp .env.example .env   # fill in a test bot token and your chat ID
   python main.py
   ```
6. Add an entry to `CHANGELOG.md` under `[Unreleased]`.
7. Never commit `.env`, `state.json` or anything else listed in `.gitignore`.
8. Describe in the pull request what changed and how you tested it.

## Code of conduct

Be respectful. Harassment or personal attacks are not welcome.
