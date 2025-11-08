from uuid import UUID
import pydantic


class LLMresponses(pydantic.BaseModel):
    responses: list[LLMResponseId]


class LLMResponse(pydantic.BaseModel):
    summary: str
    action_items: list[str]


class LLMResponseId(LLMResponse):
    id: UUID


class Transcript(pydantic.BaseModel):
    text: str

    @pydantic.field_validator("text", mode="before")
    @classmethod
    def _strip_text(cls, v: str) -> str:
        if len(value := v.strip()) == 0:
            raise ValueError("Transcript cannot be empty")
        return value


class Transcripts(pydantic.BaseModel):
    transcripts: list[Transcript]
