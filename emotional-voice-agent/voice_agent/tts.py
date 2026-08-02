"""Cartesia TTS layer: turns emotion-tagged segments into audio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .brain import Reply
from .config import Config
from .emotions import DEFAULT_EMOTION, emotion_tag


def build_transcript(reply: Reply) -> str:
    """Interleave Cartesia inline emotion tags with the spoken text.

    Neutral segments carry no tag — Cartesia's default delivery is neutral,
    and fewer tags means fewer chances to fight the transcript.
    """
    parts: list[str] = []
    previous_emotion: str | None = None
    for segment in reply.segments:
        if segment.emotion != DEFAULT_EMOTION and segment.emotion != previous_emotion:
            parts.append(f"{emotion_tag(segment.emotion)} {segment.text}")
        else:
            parts.append(segment.text)
        previous_emotion = segment.emotion
    return " ".join(parts)


@dataclass
class Speaker:
    cfg: Config

    def __post_init__(self) -> None:
        from cartesia import Cartesia

        self._client = Cartesia(api_key=self.cfg.cartesia_api_key)

    def synthesize(self, reply: Reply, out_path: Path) -> Path:
        """Generate a WAV file for the reply and return its path."""
        response = self._client.tts.generate(
            model_id=self.cfg.tts_model,
            transcript=build_transcript(reply),
            voice={"mode": "id", "id": self.cfg.voice_id},
            output_format={
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": self.cfg.sample_rate,
            },
            language=self.cfg.language,
        )
        response.write_to_file(str(out_path))
        return out_path
