from app.adapters import db

import pytest


def test_db_crud_sync_basic() -> None:
    database = db.DB()

    created = database.create({"a": 1})
    assert "id" in created and created["a"] == 1

    fetched = database.get(created["id"])  # type: ignore[index]
    assert fetched == created

    updated = database.update(created["id"], {"a": 2})  # type: ignore[index]
    assert updated is not None
    assert updated["a"] == 2 and updated["id"] == created["id"]  # type: ignore[index]

    # missing branches
    assert database.update("missing", {"a": 3}) is None
    assert database.get("missing") is None

    assert database.delete(created["id"]) is True  # type: ignore[index]
    assert database.delete("missing") is False

    assert database.all() == []


@pytest.mark.asyncio
async def test_db_crud_async_basic() -> None:
    database = db.DB()

    created = await database.acreate({"a": 1})
    assert "id" in created and created["a"] == 1

    fetched = await database.aget(created["id"])  # type: ignore[index]
    assert fetched == created

    updated = await database.aupdate(created["id"], {"a": 2})  # type: ignore[index]
    assert updated is not None
    assert updated["a"] == 2 and updated["id"] == created["id"]  # type: ignore[index]

    all_items = await database.aall()
    assert len(all_items) == 1

    assert await database.adelete(created["id"]) is True  # type: ignore[index]
    assert await database.adelete("missing") is False


@pytest.mark.asyncio
async def test_db_bulk_acreate() -> None:
    database = db.DB()

    payload = [{"n": i} for i in range(3)]
    results = await database.bulk_acreate(payload)

    ids = [r["id"] for r in results]
    assert len(set(ids)) == 3
    assert all("id" in r and "n" in r for r in results)
