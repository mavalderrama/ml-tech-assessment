import pytest
import pydantic

from app.ports import llm as llm_port
from app.ports import manager as manager_port
from app.ports import repository as repository_port


class _DummyDTO(pydantic.BaseModel):
    value: int | None = None


class DummyLLM(llm_port.LLm):
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]):
        # Intentionally call into the abstract base to execute the 'pass' line for coverage
        super().run_completion(system_prompt, user_prompt, dto)
        return None  # type: ignore[return-value]

    async def run_completion_async(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]):
        # Intentionally call into the abstract base to execute the 'pass' line for coverage
        await super().run_completion_async(system_prompt, user_prompt, dto)
        return None  # type: ignore[return-value]


def test_llm_abstract_methods_can_be_called_via_super():
    impl = DummyLLM()
    # Just ensure calls run and return None, executing base 'pass' statements
    assert impl.run_completion("s", "u", _DummyDTO) is None


@pytest.mark.asyncio
async def test_llm_async_abstract_method_via_super():
    impl = DummyLLM()
    assert await impl.run_completion_async("s", "u", _DummyDTO) is None


class DummyManager(manager_port.Manager):
    def summarize(self, text):  # type: ignore[override]
        # Exercise base abstract 'pass' line
        super().summarize(text)
        return None

    async def asummarize(self, documents):  # type: ignore[override]
        # Exercise base abstract 'pass' line
        await super().asummarize(documents)
        return None


def test_manager_abstract_methods_via_super():
    mgr = DummyManager()
    assert mgr.summarize(object()) is None


@pytest.mark.asyncio
async def test_manager_async_abstract_methods_via_super():
    mgr = DummyManager()
    assert await mgr.asummarize(object()) is None


class DummyRepository(repository_port.Repository):
    # Each method will purposefully delegate to the abstract method to trigger NotImplementedError
    def create(self, data):  # type: ignore[override]
        return super().create(data)

    def get(self, obj_id):  # type: ignore[override]
        return super().get(obj_id)

    def update(self, obj_id, data):  # type: ignore[override]
        return super().update(obj_id, data)

    def delete(self, obj_id):  # type: ignore[override]
        return super().delete(obj_id)

    def all(self):  # type: ignore[override]
        return super().all()

    async def acreate(self, data):  # type: ignore[override]
        return await super().acreate(data)

    async def bulk_acreate(self, data):  # type: ignore[override]
        return await super().bulk_acreate(data)

    async def aget(self, obj_id):  # type: ignore[override]
        return await super().aget(obj_id)

    async def aupdate(self, obj_id, data):  # type: ignore[override]
        return await super().aupdate(obj_id, data)

    async def adelete(self, obj_id):  # type: ignore[override]
        return await super().adelete(obj_id)

    async def aall(self):  # type: ignore[override]
        return await super().aall()


def test_repository_sync_abstract_methods_raise_notimplemented():
    repo = DummyRepository()
    with pytest.raises(NotImplementedError):
        repo.create({})
    with pytest.raises(NotImplementedError):
        repo.get("1")
    with pytest.raises(NotImplementedError):
        repo.update("1", {})
    with pytest.raises(NotImplementedError):
        repo.delete("1")
    with pytest.raises(NotImplementedError):
        repo.all()


@pytest.mark.asyncio
async def test_repository_async_abstract_methods_raise_notimplemented():
    repo = DummyRepository()
    with pytest.raises(NotImplementedError):
        await repo.acreate({})
    with pytest.raises(NotImplementedError):
        await repo.bulk_acreate([])
    with pytest.raises(NotImplementedError):
        await repo.aget("1")
    with pytest.raises(NotImplementedError):
        await repo.aupdate("1", {})
    with pytest.raises(NotImplementedError):
        await repo.adelete("1")
    with pytest.raises(NotImplementedError):
        await repo.aall()
