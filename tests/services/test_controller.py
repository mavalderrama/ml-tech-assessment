import sys
import types
import asyncio
import pytest

from app.services.controller import Controller
from app.domain import dtos
from app.adapters import db as db_module
from app.adapters import db


class FakeLLM:
    def run_completion(
        self, system_prompt: str, user_prompt: str, dto: type[dtos.LLMResponse]
    ):
        return dto(summary="sum", action_items=["x"])  # type: ignore[call-arg]

    async def run_completion_async(
        self, system_prompt: str, user_prompt: str, dto: type[dtos.LLMResponse]
    ):
        await asyncio.sleep(0)
        return dto(summary="asum", action_items=["ax"])  # type: ignore[call-arg]


@pytest.fixture()
def fresh_db(monkeypatch: pytest.MonkeyPatch):
    # Patch the global database used inside the controller module
    monkeypatch.setattr(db_module, "database", db.DB(), raising=True)
    return db_module.database


def test_controller_summarize_sync(fresh_db) -> None:  # type: ignore[no-redef]
    ctl = Controller(llm_client=FakeLLM())

    resp = ctl.summarize(dtos.Transcript(text="hello"))

    assert resp.summary == "sum"
    assert resp.action_items == ["x"]
    assert hasattr(resp, "id")


@pytest.mark.asyncio
async def test_controller_summarize_async(fresh_db) -> None:  # type: ignore[no-redef]
    ctl = Controller(llm_client=FakeLLM())

    docs = dtos.Transcripts(
        transcripts=[dtos.Transcript(text="a"), dtos.Transcript(text="b")]
    )
    out = await ctl.asummarize(docs)

    assert len(out.responses) == 2
    assert all(r.summary in ("asum", "sum", "asum") for r in out.responses)


def test_controller_get_summary(fresh_db) -> None:  # type: ignore[no-redef]
    # seed one record
    created = db_module.database.create({"summary": "s", "action_items": ["a"]})

    ctl = Controller(llm_client=FakeLLM())
    got = ctl.get_summary(created["id"])  # type: ignore[index]

    assert got.summary == "s"
    assert got.action_items == ["a"]
    assert str(got.id) == created["id"]  # type: ignore[literal-required]
