import discord

from discord_commit_tracker.embeds import build_push_embed

SINGLE_COMMIT = [
    {"id": "def456abc", "message": "Add README", "author": {"name": "Monalisa Octocat"}}
]


def _build(**kwargs):
    defaults = dict(
        repo_full_name="octocat/hello-world",
        repo_url="https://github.com/octocat/hello-world",
        compare_url="https://github.com/octocat/hello-world/compare/abc...def",
        branch="main",
        commits=SINGLE_COMMIT,
        latest_timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    defaults.update(kwargs)
    return build_push_embed(**defaults)


def test_embed_is_discord_embed():
    assert isinstance(_build(), discord.Embed)


def test_embed_title_includes_commit_count_and_repo():
    embed = _build()
    assert "1" in embed.title
    assert "octocat/hello-world" in embed.title


def test_embed_links_to_compare_url():
    embed = _build()
    assert embed.url == "https://github.com/octocat/hello-world/compare/abc...def"


def test_embed_description_contains_commit_info():
    embed = _build()
    assert "def456a" in embed.description  # short sha
    assert "Add README" in embed.description
    assert "Monalisa Octocat" in embed.description


def test_embed_commit_message_truncated_at_72_chars():
    long_message = "A" * 100
    embed = _build(commits=[{"id": "abc123", "message": long_message, "author": {"name": "Alice"}}])
    for line in embed.description.splitlines():
        if "abc123" in line:
            # message portion must be truncated — line contains sha, msg, author
            assert long_message not in line


def test_embed_private_repo_has_footer():
    embed = _build(private=True)
    assert embed.footer is not None
    assert "Private repo" in embed.footer.text


def test_embed_public_repo_no_footer():
    embed = _build(private=False)
    assert embed.footer.text is None


def test_embed_multi_commit_lists_all():
    commits = [
        {"id": "aaa111", "message": "First", "author": {"name": "Alice"}},
        {"id": "bbb222", "message": "Second", "author": {"name": "Bob"}},
    ]
    embed = _build(commits=commits)
    assert "aaa111" in embed.description
    assert "bbb222" in embed.description
    assert "2" in embed.title
