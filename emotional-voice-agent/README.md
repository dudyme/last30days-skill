# Emotional Voice Agent

A conversational voice agent that responds in a **highly emotional voice**, built on
[Cartesia](https://cartesia.ai) expressive TTS and a Claude conversation brain.

How a turn works:

1. **Listen** — you type, or speak (`--voice-in`: mic → Cartesia `ink-whisper` STT).
2. **Think** — Claude replies as emotion-tagged segments: each one or two sentences
   carry an emotion (`excited`, `sympathetic`, `sad`, …) that genuinely matches the words.
3. **Speak** — the segments become a Cartesia Sonic transcript with inline emotion tags
   (`<emotion value="excited"/> …`), so the delivery shifts feeling *mid-reply*, and the
   audio plays back.

The emotion never comes from a fixed setting — the brain chooses it per segment, which is
what makes the voice land as emotional rather than merely styled.

## Setup

```bash
cd emotional-voice-agent
cp .env.example .env       # fill in CARTESIA_API_KEY and ANTHROPIC_API_KEY
uv venv && uv pip install -e ".[audio,dev]"
```

`[audio]` (sounddevice + numpy) is only needed for mic input and in-process playback;
without it, replies are saved as WAV files (and played via `afplay`/`aplay`/`ffplay` when
available).

## Run

```bash
uv run voice-agent                 # typed input, spoken emotional replies
uv run voice-agent --voice-in      # full voice loop (mic + STT)
uv run voice-agent --save-audio out/   # keep the generated WAVs
```

Example turn:

```
you: I finally got the job offer today!
agent [excited]: No way — you got it?! That's incredible!
agent [affectionate]: I'm genuinely so happy for you. You worked hard for this.
```

## Configuration

All via environment variables (or `.env` — see `.env.example`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `CARTESIA_API_KEY` | — | required, Cartesia TTS + STT |
| `ANTHROPIC_API_KEY` | — | required, conversation brain |
| `CARTESIA_TTS_MODEL` | `sonic-3.5` | Cartesia TTS model alias |
| `CARTESIA_VOICE_ID` | docs default voice | pick an emotive voice (Leo, Jace, Kyle, Gavin, Maya, Tessa, Dana, Marian) from the Voice Library |
| `CARTESIA_STT_MODEL` | `ink-whisper` | batch STT model |
| `VOICE_AGENT_LLM_MODEL` | `claude-sonnet-5` | Claude model for the brain |
| `VOICE_AGENT_LANGUAGE` | `en` | TTS/STT language |
| `VOICE_AGENT_PERSONA` | warm companion | system-prompt persona |

## Tests

```bash
uv run pytest
```

Tests cover the offline logic — emotion normalization, reply parsing, and transcript
building — and need no API keys or network.

## Notes on emotion quality

- Cartesia treats emotion tags as guidance: they only convince when the emotion matches
  the words. The system prompt enforces that agreement on the Claude side.
- Neutral segments are left untagged, and consecutive same-emotion segments share one
  tag, so the transcript stays clean.
- For the strongest results Cartesia recommends the primary emotions (`neutral`, `calm`,
  `angry`, `content`, `sad`, `scared`); the agent also uses a curated extended set
  (see `voice_agent/emotions.py`).
