"""Conversation loop: listen (or read), think with Claude, speak with emotion."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from .audio import play_wav, record_wav
from .brain import Brain
from .config import Config
from .stt import Transcriber
from .tts import Speaker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="voice-agent",
        description="Emotional voice agent (Claude brain + Cartesia expressive TTS).",
    )
    parser.add_argument(
        "--voice-in",
        action="store_true",
        help="Use the microphone + Cartesia STT for input (default: typed input)",
    )
    parser.add_argument(
        "--save-audio",
        type=Path,
        default=None,
        help="Directory to keep generated WAV replies (default: temp files)",
    )
    args = parser.parse_args(argv)

    cfg = Config.from_env()
    cfg.require_keys()

    brain = Brain(cfg)
    speaker = Speaker(cfg)
    transcriber = Transcriber(cfg) if args.voice_in else None

    out_dir = args.save_audio or Path(tempfile.mkdtemp(prefix="voice-agent-"))
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Emotional voice agent ready. Ctrl-C or 'quit' to exit.\n")
    turn = 0
    while True:
        try:
            if transcriber:
                wav_in = record_wav(out_dir / f"input-{turn:03d}.wav")
                user_text = transcriber.transcribe(wav_in)
                if not user_text:
                    print("(heard nothing, try again)")
                    continue
                print(f"you: {user_text}")
            else:
                user_text = input("you: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye!")
            return 0
        if not user_text:
            continue
        if user_text.lower() in {"quit", "exit", "bye"}:
            print("bye!")
            return 0

        reply = brain.respond(user_text)
        for segment in reply.segments:
            print(f"agent [{segment.emotion}]: {segment.text}")

        wav_out = speaker.synthesize(reply, out_dir / f"reply-{turn:03d}.wav")
        if not play_wav(wav_out):
            print(f"(no audio device — reply saved to {wav_out})")
        turn += 1


if __name__ == "__main__":
    sys.exit(main())
