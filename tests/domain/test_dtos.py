from uuid import uuid4
from app.domain import dtos


def test_llmresponse_and_id_models() -> None:
    r = dtos.LLMResponse(summary="s", action_items=["a", "b"])
    d = r.model_dump()
    assert d == {"summary": "s", "action_items": ["a", "b"]}

    uid = uuid4()
    rid = dtos.LLMResponseId(id=uid, summary="s", action_items=["a"])
    dumped = rid.model_dump()
    assert str(uid) == str(dumped["id"])  # type: ignore[index]


def test_transcript_models() -> None:
    t = dtos.Transcript(text="hello")
    assert t.text == "hello"

    ts = dtos.Transcripts(transcripts=[t, dtos.Transcript(text="world")])
    assert [x.text for x in ts.transcripts] == ["hello", "world"]


def test_llmresponses_collection() -> None:
    uid1, uid2 = uuid4(), uuid4()
    r1 = dtos.LLMResponseId(id=uid1, summary="a", action_items=["x"])  # type: ignore[call-arg]
    r2 = dtos.LLMResponseId(id=uid2, summary="b", action_items=["y"])  # type: ignore[call-arg]

    bag = dtos.LLMresponses(responses=[r1, r2])
    assert len(bag.responses) == 2
    assert bag.responses[0].summary == "a"
