import asyncio
from typing import Any

import pydantic
import pytest

from app.domain import configurations
from tests.adapters import mock_data
from app.adapters import openai as openai_adapter_module
from app.domain import dtos


class _DummyMessage:
    def __init__(self, dto_cls: type[pydantic.BaseModel]):
        self.parsed = dto_cls(summary="ok", action_items=["a", "b"])  # type: ignore[call-arg]


class _DummyChoice:
    def __init__(self, dto_cls: type[pydantic.BaseModel]):
        self.message = _DummyMessage(dto_cls)


class _DummyCompletion:
    def __init__(self, dto_cls: type[pydantic.BaseModel]):
        self.choices = [_DummyChoice(dto_cls)]


class _SyncCompletions:
    def parse(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        response_format: type[pydantic.BaseModel],
    ):
        return _DummyCompletion(response_format)


class _AsyncCompletions:
    async def parse(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        response_format: type[pydantic.BaseModel],
    ):
        await asyncio.sleep(0)
        return _DummyCompletion(response_format)


class _SyncClient:
    def __init__(self, api_key: str):
        self.beta = type(
            "Beta", (), {"chat": type("Chat", (), {"completions": _SyncCompletions()})}
        )()


class _AsyncClient:
    def __init__(self, api_key: str):
        self.beta = type(
            "Beta", (), {"chat": type("Chat", (), {"completions": _AsyncCompletions()})}
        )()


@pytest.fixture(autouse=True)
def _patch_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch the openai clients used inside the adapter
    monkeypatch.setattr(
        openai_adapter_module.openai, "OpenAI", _SyncClient, raising=True
    )
    monkeypatch.setattr(
        openai_adapter_module.openai, "AsyncOpenAI", _AsyncClient, raising=True
    )


def test_openai_adapter_sync() -> None:
    env_variables = configurations.AppSettings()

    system_prompt = mock_data.SYSTEM_PROMPT
    user_prompt = mock_data.RAW_USER_PROMPT.format(transcript=mock_data.TRANSCRIPT)

    adapter = openai_adapter_module.OpenAIAdapter(
        env_variables.OPENAI_API_KEY, env_variables.OPENAI_MODEL
    )

    response = adapter.run_completion(system_prompt, user_prompt, dtos.LLMResponse)
    data = response.model_dump()

    assert data["summary"] == "ok"
    assert data["action_items"] == ["a", "b"]


@pytest.mark.asyncio
async def test_openai_adapter_async() -> None:
    env_variables = configurations.AppSettings()

    system_prompt = mock_data.SYSTEM_PROMPT
    user_prompt = mock_data.RAW_USER_PROMPT.format(transcript=mock_data.TRANSCRIPT)

    adapter = openai_adapter_module.OpenAIAdapter(
        env_variables.OPENAI_API_KEY, env_variables.OPENAI_MODEL
    )

    response = await adapter.run_completion_async(
        system_prompt, user_prompt, dtos.LLMResponse
    )
    data = response.model_dump()

    assert data["summary"] == "ok"
    assert data["action_items"] == ["a", "b"]
