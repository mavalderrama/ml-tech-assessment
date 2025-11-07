import pydantic
from uuid import UUID


class LLMresponses(pydantic.BaseModel):
    responses: list[LLMResponseId]


class LLMResponse(pydantic.BaseModel):
    summary: str
    action_items: list[str]


class LLMResponseId(LLMResponse):
    id: UUID


class Transcript(pydantic.BaseModel):
    text: str


class Transcripts(pydantic.BaseModel):
    transcripts: list[Transcript]
