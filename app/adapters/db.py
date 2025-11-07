import uuid
import threading
import asyncio
from typing import Any
from app.ports import repository


class DB(repository.Repository):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

        self._lock = threading.Lock()
        self._alock = asyncio.Lock()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        new_id = str(uuid.uuid4())
        record = dict(data)
        record["id"] = new_id
        with self._lock:
            self._store[new_id] = record
        return record

    def get(self, obj_id: str) -> dict[str, Any] | None:
        with self._lock:
            obj = self._store.get(obj_id)
            return dict(obj) if obj is not None else None

    def update(
        self,
        obj_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        with self._lock:
            if obj_id not in self._store:
                return None
            current = dict(self._store[obj_id])
            current.update(data)
            current["id"] = obj_id  # enforce id
            self._store[obj_id] = current
            return dict(current)

    def delete(self, obj_id: str) -> bool:
        with self._lock:
            if obj_id in self._store:
                del self._store[obj_id]
                return True
            return False

    def all(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(v) for v in self._store.values()]

    async def acreate(self, data: dict[str, Any]) -> dict[str, Any]:
        new_id = str(uuid.uuid4())
        record = dict(data)
        record["id"] = new_id
        async with self._alock:
            self._store[new_id] = record
        return record

    async def bulk_acreate(
        self,
        data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return await asyncio.gather(*[self.acreate(d) for d in data])

    async def aget(self, obj_id: str) -> dict[str, Any] | None:
        async with self._alock:
            obj = self._store.get(obj_id)
            return dict(obj) if obj is not None else None

    async def aupdate(
        self,
        obj_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        async with self._alock:
            if obj_id not in self._store:
                return None
            current = dict(self._store[obj_id])
            current.update(data)
            current["id"] = obj_id
            self._store[obj_id] = current
            return dict(current)

    async def adelete(self, obj_id: str) -> bool:
        async with self._alock:
            if obj_id in self._store:
                del self._store[obj_id]
                return True
            return False

    async def aall(self) -> list[dict[str, Any]]:
        async with self._alock:
            return [dict(v) for v in self._store.values()]


database = DB()
