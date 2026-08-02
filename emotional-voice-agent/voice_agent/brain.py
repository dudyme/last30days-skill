"""Conversation brain: Claude decides *what* to say and *how it should feel*.

The model replies as JSON segments, each tagged with one supported emotion, so
the TTS layer can interleave Cartesia emotion tags mid-response — an answer can
open excited, turn sympathetic, and land calm.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .config import Config
from .emotions import SUPPORTED_EMOTIONS, normalize_emotion


@dataclass
class Segment:
    emotion: str
    text: str


@dataclass
class Reply:
    segments: list[Segment]

    @property
    def plain_text(self) -> str:
        return " ".join(s.text for s in self.segments)


SYSTEM_PROMPT_TEMPLATE = """\
{persona}

You are speaking aloud through an expressive text-to-speech voice, so write
the way people talk: short sentences, contractions, no markdown, no lists,
no stage directions. Never mention emotions, tags, or JSON to the user.

Respond ONLY with a JSON object of this exact shape:
{{"segments": [{{"emotion": "<emotion>", "text": "<one or two spoken sentences>"}}]}}

Rules for segments:
- 1 to 4 segments per reply. Split when the feeling shifts mid-reply.
- "emotion" must be one of: {emotions}.
- The emotion must genuinely match the words in that segment — the voice
  engine only sounds convincing when text and emotion agree.
- Be vividly emotional: react, empathize, celebrate, worry along with the
  user. Avoid flat neutral delivery unless the content truly is neutral.
"""


def build_system_prompt(cfg: Config) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        persona=cfg.persona,
        emotions=", ".join(sorted(SUPPORTED_EMOTIONS)),
    )


def parse_reply(raw: str) -> Reply:
    """Parse the model's JSON reply, degrading gracefully on malformed output."""
    text = raw.strip()
    # Strip a markdown code fence if the model added one despite instructions.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    try:
        data = json.loads(text)
        segments = [
            Segment(
                emotion=normalize_emotion(item.get("emotion")),
                text=str(item.get("text", "")).strip(),
            )
            for item in data.get("segments", [])
            if str(item.get("text", "")).strip()
        ]
        if segments:
            return Reply(segments=segments)
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    # Fallback: speak the raw text with neutral delivery rather than failing.
    return Reply(segments=[Segment(emotion="neutral", text=raw.strip())])


@dataclass
class Brain:
    cfg: Config
    history: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=self.cfg.anthropic_api_key)

    def respond(self, user_text: str) -> Reply:
        self.history.append({"role": "user", "content": user_text})
        response = self._client.messages.create(
            model=self.cfg.llm_model,
            max_tokens=1024,
            system=build_system_prompt(self.cfg),
            messages=self.history,
        )
        raw = "".join(block.text for block in response.content if block.type == "text")
        self.history.append({"role": "assistant", "content": raw})
        return parse_reply(raw)
