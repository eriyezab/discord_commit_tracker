import os
import tempfile

from discord_commit_tracker.db import Database


async def test_db_file_created_at_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.sqlite3")
        assert not os.path.exists(db_path)

        db = Database(db_path)
        await db.init()
        await db.close()

        assert os.path.exists(db_path)
