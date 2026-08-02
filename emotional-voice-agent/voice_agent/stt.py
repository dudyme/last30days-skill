"""Speech-to-text via Cartesia batch STT (ink-whisper)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import Config


@dataclass
class Transcriber:
    cfg: Config

    def __post_init__(self) -> None:
        from cartesia import Cartesia

        self._client = Cartesia(api_key=self.cfg.cartesia_api_key)

    def transcribe(self, wav_path: Path) -> str:
        with open(wav_path, "rb") as f:
            result = self._client.stt.transcribe(
                file=f,
                model=self.cfg.stt_model,
                language=self.cfg.language,
            )
        return (getattr(result, "text", None) or "").strip()
