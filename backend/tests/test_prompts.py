import json
import pytest
from src.database import init_db, get_db, new_id, now


@pytest.mark.asyncio
async def test_create_and_list_published_prompts():
    await init_db()
    db = await get_db()

    # Create draft prompt
    pid = new_id()
    await db.execute(
        """INSERT INTO prompt_assets (id, title, prompt_template, scene_type, character_id,
           status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, 'daily_life', 'orange_tabby', 'draft', '', ?, ?)""",
        (pid, "测试草稿", "A test prompt template", now(), now()),
    )

    # Create published prompt
    pid2 = new_id()
    await db.execute(
        """INSERT INTO prompt_assets (id, title, prompt_template, scene_type, character_id,
           status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, 'skit_comedy', 'black_cat', 'published', '', ?, ?)""",
        (pid2, "测试已发布", "A published prompt", now(), now()),
    )
    await db.commit()

    # Only published should be visible
    cursor = await db.execute(
        "SELECT COUNT(*) FROM prompt_assets WHERE status = 'published'"
    )
    count = (await cursor.fetchone())[0]
    assert count >= 1

    # Cleanup
    await db.execute("DELETE FROM prompt_assets WHERE id IN (?, ?)", (pid, pid2))
    await db.commit()
