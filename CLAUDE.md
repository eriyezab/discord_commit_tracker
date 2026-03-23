# Discord Commit Tracker — Project Instructions

## Package Manager: uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. uv is faster than pip and produces a `uv.lock` lockfile that pins exact versions for reproducible installs.

**Install uv once globally (if not already installed):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install all dependencies (creates `.venv` automatically):**

```bash
uv sync --extra dev
```

**Run any command inside the venv:**

```bash
uv run pytest
uv run python -m discord_commit_tracker.main
```

Never use the system `python3` or `pip3` directly. Always use `uv run <command>` or `uv sync`.

## Pre-commit Hooks

This project uses pre-commit hooks to run ruff lint and format checks before every commit.

**Install hooks after cloning (one-time setup):**

```bash
uv run pre-commit install
```

Hooks run automatically on `git commit`. To run manually against all files:

```bash
uv run pre-commit run --all-files
```

## Running Tests

```bash
uv run pytest
```

## Project Structure

- `discord_commit_tracker/` — application source
- `tests/` — pytest test suite
- `docs/` — spec and project plan
- `.env` — local environment variables (never committed)
- `uv.lock` — pinned dependency versions (always commit this)

## Session Continuity

YOU MUST commit immediately after marking any task as completed — no exceptions, no batching. Do not move on to the next task until the commit is done.

The commit message MUST include the current state of the task list — which tasks are done, in progress, and pending. This allows future sessions to resume from exactly where work left off by reading the latest commit on the branch.

Format the task list in the commit body like:

```
Tasks:
[x] Task one
[x] Task two
[ ] Task three (next)
[ ] Task four
```

## Pull Requests

YOU MUST create a PR at the end of every completed milestone — no exceptions.

Every PR description MUST include:
- A summary of what was built
- The full task list showing completed items (copied from the commit messages)
- A test plan (automated tests that pass + any manual verification steps)

## Environment Variables

Required in `.env` for local development:
- `DISCORD_TOKEN` — bot token from Discord Developer Portal
- `DISCORD_GUILD_ID` — Discord server ID
- `DISCORD_CHANNEL_ID` — channel the bot posts to
- `PORT` — uvicorn port (default: `8000`)
- `DATABASE_PATH` — SQLite file path (default: `db.sqlite3`)
- `WEBHOOK_BASE_URL` — public base URL (set via ngrok in dev)
