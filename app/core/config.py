"""Application settings (model name, Ollama URL, timeouts) loaded from env."""

from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentinel Health"
    app_version: str = "0.1.0"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e4b-it-q4_K_M"
    # 180s accommodates first-call vision-weight loading + multimodal inference.
    # Subsequent calls with keep_alive should finish in ~5-15s on M-series GPU.
    ollama_timeout_seconds: float = 180.0
    ollama_temperature: float = 0.2
    # How long Ollama keeps the model resident in VRAM between requests.
    # Set to a long value so the second image-call is fast (model already warm).
    ollama_keep_alive: str = "30m"

    hub_physician_phone: str = ""
    hub_physician_name: str = "Hub Physician"
    # Optional: name of the WhatsApp group used as the actual hub (matches the
    # real-world PHC workflow — escalation gets pasted into the group, not DM'd).
    # If set, the demo UI surfaces a "Copy to <group>" button alongside the
    # single-contact Send button. Example: "TVMCH Cardiology Hub and Spoke".
    hub_group_name: str = ""
    facility_name: str = "Spoke clinic"
    chw_name: str = ""

    # Transport context for RED escalation: distance + average ambulance
    # speed → ETA. The CHW also gets a small input to enter the assigned
    # ambulance number, which gets embedded in the WhatsApp handoff text.
    nearest_hub_km: float = 0.0
    avg_ambulance_kmh: float = 50.0

    reports_enabled: bool = True
    reports_path: str = "data/reports/reports.jsonl"
    reports_list_default_limit: int = 50

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
