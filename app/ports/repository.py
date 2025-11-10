from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Repository(ABC):
    """Repository interface."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get(self, obj_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update(self, obj_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def all(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    # ───── async ─────
    @abstractmethod
    async def acreate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def bulk_acreate(
        self,
        data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def aget(self, obj_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def aupdate(self, obj_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def adelete(self, obj_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def aall(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
