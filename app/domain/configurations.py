import pydantic_settings


class AppSettings(pydantic_settings.BaseSettings):
    """Application settings."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OPENAI_API_KEY: str = "no-key-4-u"
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"


app_settings = AppSettings()
