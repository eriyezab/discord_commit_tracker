import pytest

from discord_commit_tracker.config import Config, ConfigError

REQUIRED_VARS = {
    "DISCORD_TOKEN": "test-token",
    "DISCORD_CHANNEL_ID": "111",
    "DISCORD_GUILD_ID": "222",
}


def test_loads_required_vars(monkeypatch):
    for key, val in REQUIRED_VARS.items():
        monkeypatch.setenv(key, val)

    config = Config.from_env()

    assert config.discord_token == "test-token"
    assert config.discord_channel_id == "111"
    assert config.discord_guild_id == "222"


def test_defaults(monkeypatch):
    for key, val in REQUIRED_VARS.items():
        monkeypatch.setenv(key, val)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("WEBHOOK_BASE_URL", raising=False)

    config = Config.from_env()

    assert config.port == 8000
    assert config.database_path == "db.sqlite3"
    assert config.webhook_base_url == ""


def test_overrides_defaults(monkeypatch):
    for key, val in REQUIRED_VARS.items():
        monkeypatch.setenv(key, val)
    monkeypatch.setenv("PORT", "3000")
    monkeypatch.setenv("DATABASE_PATH", "/data/bot.db")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "https://example.com")

    config = Config.from_env()

    assert config.port == 3000
    assert config.database_path == "/data/bot.db"
    assert config.webhook_base_url == "https://example.com"


@pytest.mark.parametrize("missing_var", list(REQUIRED_VARS.keys()))
def test_missing_required_var_raises(monkeypatch, missing_var):
    for key, val in REQUIRED_VARS.items():
        monkeypatch.setenv(key, val)
    monkeypatch.delenv(missing_var)

    with pytest.raises(ConfigError, match=missing_var):
        Config.from_env()
