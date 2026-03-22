# Discord Commit Tracker — Project Plan

This plan breaks the v1 MVP into discrete, shippable milestones. Each milestone has a clear goal and a checklist of tasks. Work through them in order — each builds on the last.

---

## Milestone 1: Project Scaffold

**Goal:** Runnable skeleton with both the Discord bot and FastAPI server starting up together.

- [ ] Initialize Python project (`pyproject.toml` or `requirements.txt`)
- [ ] Install dependencies: `discord.py`, `fastapi`, `uvicorn`, `aiosqlite`
- [ ] Create entry point (`main.py`) that runs FastAPI (uvicorn) and discord.py concurrently on a shared asyncio event loop
- [ ] Add a `GET /health` endpoint that returns `200 OK`
- [ ] Load config from environment variables (`DISCORD_TOKEN`, `DISCORD_CHANNEL_ID`, `DISCORD_GUILD_ID`, `PORT`, `DATABASE_PATH`, `WEBHOOK_BASE_URL`)
- [ ] Confirm bot connects to Discord and server starts on the correct port

---

## Milestone 2: Database Setup

**Goal:** SQLite database initialized and ready for repo tracking.

- [ ] Create `db.py` module with async database connection setup (aiosqlite)
- [ ] Run schema migration on startup to create the `tracked_repos` table if it doesn't exist
- [ ] Add helper functions: `add_repo`, `remove_repo`, `get_repo`, `list_repos`
- [ ] Confirm DB file is created at `DATABASE_PATH` on startup

---

## Milestone 3: Hardcoded Webhook → Discord Embed

**Goal:** Prove the end-to-end flow without slash commands or DB lookups.

- [ ] Implement `POST /github/webhook` endpoint
- [ ] Parse the raw JSON payload and extract commit data (`commits`, `repository`, `ref`)
- [ ] Format a Discord embed for a single commit (author, message, repo link, diff link, timestamp)
- [ ] Post the embed to the configured channel
- [ ] Use ngrok to expose the local server
- [ ] Manually add a webhook to a test GitHub repo (no secret verification yet)
- [ ] Push a test commit and confirm the embed appears in Discord

---

## Milestone 4: Slash Commands

**Goal:** Users can track and untrack repos via Discord slash commands.

- [ ] Register slash commands with the Discord guild on bot startup
- [ ] Implement `/track <owner/repo>`:
  - Validate `owner/repo` format
  - Generate a webhook secret (`secrets.token_hex(32)`)
  - Save repo to the database
  - Respond ephemerally with the webhook URL, secret, and GitHub setup instructions
- [ ] Implement `/untrack <owner/repo>`:
  - Remove repo from database
  - Respond with confirmation and reminder to delete the webhook from GitHub
- [ ] Implement `/list`:
  - Query all tracked repos
  - Respond with the list, or a "none tracked" message

---

## Milestone 5: Signature Verification & Security

**Goal:** The webhook endpoint only processes requests from legitimate GitHub sources.

- [ ] On incoming `POST /github/webhook`, extract `X-Hub-Signature-256` header
- [ ] Extract `repository.full_name` from the payload
- [ ] Look up the repo in the database to retrieve its `webhook_secret`
- [ ] Verify the HMAC-SHA256 signature using `hmac.compare_digest`
- [ ] Return `401 Unauthorized` on signature mismatch
- [ ] Return `200 OK` silently if the repo is not found in the database (no information leak)

---

## Milestone 6: Event Filtering & Embed Polish

**Goal:** Only relevant pushes are posted, with complete embed formatting.

- [ ] Skip non-push events: check `X-GitHub-Event` header, return `200 OK` and ignore if not `push`
- [ ] Skip pushes to non-default branches: compare `ref` against `repository.default_branch`
- [ ] Handle multi-commit pushes: post one embed per commit
- [ ] Cap at 5 embeds per push: if more than 5 commits, post the 5 most recent and append a "and N more — see full comparison" note linking to the `compare` URL
- [ ] Add private repo flag: if `repository.private` is `true`, add a footer note to the embed

---

## Milestone 7: Deploy to Production

**Goal:** Bot is running on a publicly reachable host with real webhook URLs.

- [ ] Choose hosting platform (Railway or Fly.io) and create a new project
- [ ] Set all environment variables in the hosting platform
- [ ] Deploy and confirm `GET /health` returns `200 OK`
- [ ] Update GitHub webhooks from ngrok URLs to the production URL
- [ ] Run `/track` in Discord to register a real repo
- [ ] Push a commit and verify the embed appears end-to-end
- [ ] Have a friend add their repo and verify their commits appear too
