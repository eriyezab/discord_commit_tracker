import discord

from discord_commit_tracker.embeds import build_commit_embed


def test_embed_has_required_fields():
    embed = build_commit_embed(
        author="Monalisa Octocat",
        message="Add README",
        repo_full_name="octocat/hello-world",
        repo_url="https://github.com/octocat/hello-world",
        commit_url="https://github.com/octocat/hello-world/commit/def456",
        timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "Monalisa Octocat"
    assert embed.title == "Add README"
    assert embed.url == "https://github.com/octocat/hello-world/commit/def456"


def test_embed_title_truncated_at_80_chars():
    long_message = "A" * 100
    embed = build_commit_embed(
        author="Author",
        message=long_message,
        repo_full_name="owner/repo",
        repo_url="https://github.com/owner/repo",
        commit_url="https://github.com/owner/repo/commit/abc",
        timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    assert len(embed.title) <= 80
    assert embed.title.endswith("...")


def test_embed_title_not_truncated_when_short():
    embed = build_commit_embed(
        author="Author",
        message="Short message",
        repo_full_name="owner/repo",
        repo_url="https://github.com/owner/repo",
        commit_url="https://github.com/owner/repo/commit/abc",
        timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    assert embed.title == "Short message"


def test_embed_private_repo_has_footer():
    embed = build_commit_embed(
        author="Author",
        message="Fix bug",
        repo_full_name="owner/private-repo",
        repo_url="https://github.com/owner/private-repo",
        commit_url="https://github.com/owner/private-repo/commit/abc",
        timestamp="2024-01-15T12:00:00Z",
        private=True,
    )
    assert embed.footer is not None
    assert "Private repo" in embed.footer.text


def test_embed_public_repo_no_footer():
    embed = build_commit_embed(
        author="Author",
        message="Fix bug",
        repo_full_name="owner/repo",
        repo_url="https://github.com/owner/repo",
        commit_url="https://github.com/owner/repo/commit/abc",
        timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    assert embed.footer.text is None


def test_embed_repo_field_links_to_repo():
    embed = build_commit_embed(
        author="Author",
        message="Fix bug",
        repo_full_name="octocat/hello-world",
        repo_url="https://github.com/octocat/hello-world",
        commit_url="https://github.com/octocat/hello-world/commit/abc",
        timestamp="2024-01-15T12:00:00Z",
        private=False,
    )
    repo_field = next(f for f in embed.fields if f.name == "Repository")
    assert "octocat/hello-world" in repo_field.value
    assert "https://github.com/octocat/hello-world" in repo_field.value
