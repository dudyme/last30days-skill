"""Configuration for the emotional voice agent.

Everything is env-driven (a `.env` file next to the project root is loaded if
present). No credentials are ever hardcoded.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv() -> None:
    """Minimal .env loader (no external dependency). Env vars already set win."""
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


@dataclass
class Config:
    cartesia_api_key: str = ""
    anthropic_api_key: str = ""
    # Stable alias for Cartesia's current expressive TTS model.
    tts_model: str = "sonic-3.5"
    # Default voice from Cartesia's docs; pick an emotive voice (Leo, Jace,
    # Kyle, Gavin, Maya, Tessa, Dana, Marian) in the Voice Library and set
    # CARTESIA_VOICE_ID to override.
    voice_id: str = "6ccbfb76-1fc6-48f7-b71d-91ac6298247b"
    stt_model: str = "ink-whisper"
    llm_model: str = "claude-sonnet-5"
    language: str = "en"
    sample_rate: int = 44100
    persona: str = field(
        default=(
            "You are a warm, vivid, highly expressive voice companion. "
            "You react with genuine feeling to what the user says."
        )
    )

    @classmethod
    def from_env(cls) -> "Config":
        _load_dotenv()
        cfg = cls(
            cartesia_api_key=os.environ.get("CARTESIA_API_KEY", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        )
        cfg.tts_model = os.environ.get("CARTESIA_TTS_MODEL", cfg.tts_model)
        cfg.voice_id = os.environ.get("CARTESIA_VOICE_ID", cfg.voice_id)
        cfg.stt_model = os.environ.get("CARTESIA_STT_MODEL", cfg.stt_model)
        cfg.llm_model = os.environ.get("VOICE_AGENT_LLM_MODEL", cfg.llm_model)
        cfg.language = os.environ.get("VOICE_AGENT_LANGUAGE", cfg.language)
        cfg.persona = os.environ.get("VOICE_AGENT_PERSONA", cfg.persona)
        return cfg

    def require_keys(self, *, need_llm: bool = True) -> None:
        missing = []
        if not self.cartesia_api_key:
            missing.append("CARTESIA_API_KEY")
        if need_llm and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if missing:
            raise SystemExit(
                "Missing required environment variables: "
                + ", ".join(missing)
                + " (see .env.example)"
            )
