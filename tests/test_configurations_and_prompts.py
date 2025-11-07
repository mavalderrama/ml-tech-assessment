from app.configurations import AppSettings
from app.domain import prompts as domain_prompts
from app import prompts as app_prompts


def test_app_settings_defaults() -> None:
    cfg = AppSettings()
    assert isinstance(cfg.OPENAI_API_KEY, str)
    assert isinstance(cfg.OPENAI_MODEL, str)
    assert cfg.OPENAI_API_KEY  # has some default content
    assert cfg.OPENAI_MODEL


def test_domain_prompts_have_placeholders() -> None:
    assert "{transcript}" in domain_prompts.RAW_USER_PROMPT
    example = domain_prompts.RAW_USER_PROMPT.format(transcript="hello")
    assert "hello" in example
    assert isinstance(domain_prompts.SYSTEM_PROMPT, str) and len(domain_prompts.SYSTEM_PROMPT) > 0


def test_app_prompts_have_placeholders() -> None:
    assert "{transcript}" in app_prompts.RAW_USER_PROMPT
    example = app_prompts.RAW_USER_PROMPT.format(transcript="hi")
    assert "hi" in example
    assert isinstance(app_prompts.SYSTEM_PROMPT, str) and len(app_prompts.SYSTEM_PROMPT) > 0
