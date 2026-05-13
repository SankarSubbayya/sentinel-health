"""Application settings (model name, Ollama URL, timeouts) loaded from env."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentinel Health"
    app_version: str = "0.1.0"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e4b-it-q4_K_M"
    ollama_timeout_seconds: float = 60.0
    ollama_temperature: float = 0.2

    hub_physician_phone: str = ""
    hub_physician_name: str = "Hub Physician"
    facility_name: str = "Spoke clinic"

    reports_enabled: bool = True
    reports_path: str = "data/reports/reports.jsonl"
    reports_list_default_limit: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
