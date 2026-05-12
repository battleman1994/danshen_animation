import json
import pytest
from src.database import init_db, get_db, new_id, now


@pytest.mark.asyncio
async def test_admin_toggle_publish():
    await init_db()
    db = await get_db()

    pid = new_id()
    await db.execute(
        """INSERT INTO prompt_assets (id, title, prompt_template, scene_type, character_id,
           status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, 'general', 'orange_tabby', 'draft', '', ?, ?)""",
        (pid, "测试提示词", "Test prompt template", now(), now()),
    )
    await db.commit()

    # Publish
    await db.execute(
        "UPDATE prompt_assets SET status = 'published', updated_at = ? WHERE id = ?",
        (now(), pid),
    )
    await db.commit()

    cursor = await db.execute("SELECT status FROM prompt_assets WHERE id = ?", (pid,))
    row = await cursor.fetchone()
    assert row["status"] == "published"

    # Unpublish
    await db.execute(
        "UPDATE prompt_assets SET status = 'draft', updated_at = ? WHERE id = ?",
        (now(), pid),
    )
    await db.commit()

    cursor = await db.execute("SELECT status FROM prompt_assets WHERE id = ?", (pid,))
    row = await cursor.fetchone()
    assert row["status"] == "draft"

    await db.execute("DELETE FROM prompt_assets WHERE id = ?", (pid,))
    await db.commit()
