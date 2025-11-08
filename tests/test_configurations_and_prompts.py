from app.domain.configurations import AppSettings
from app.domain import prompts as prompts


def test_app_settings_defaults() -> None:
    cfg = AppSettings()
    assert isinstance(cfg.OPENAI_API_KEY, str)
    assert isinstance(cfg.OPENAI_MODEL, str)
    assert cfg.OPENAI_API_KEY  # has some default content
    assert cfg.OPENAI_MODEL


def test_domain_prompts_have_placeholders() -> None:
    assert "{transcript}" in prompts.RAW_USER_PROMPT
    example = prompts.RAW_USER_PROMPT.format(transcript="hello")
    assert "hello" in example
    assert isinstance(prompts.SYSTEM_PROMPT, str) and len(prompts.SYSTEM_PROMPT) > 0


def test_app_prompts_have_placeholders() -> None:
    assert "{transcript}" in prompts.RAW_USER_PROMPT
    example = prompts.RAW_USER_PROMPT.format(transcript="hi")
    assert "hi" in example
    assert isinstance(prompts.SYSTEM_PROMPT, str) and len(prompts.SYSTEM_PROMPT) > 0
