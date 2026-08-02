"""Microphone capture and audio playback, degrading gracefully when no
audio device or player is available (e.g. headless dev boxes)."""

from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path


def play_wav(path: Path) -> bool:
    """Play a WAV file. Returns False if no playback route exists."""
    try:
        import sounddevice as sd
        import numpy as np

        with wave.open(str(path), "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            if wf.getnchannels() > 1:
                audio = audio.reshape(-1, wf.getnchannels())
            sd.play(audio, wf.getframerate())
            sd.wait()
        return True
    except Exception:
        pass
    for player in ("afplay", "aplay", "ffplay"):
        if shutil.which(player):
            cmd = [player, str(path)]
            if player == "ffplay":
                cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)]
            subprocess.run(cmd, check=False)
            return True
    return False


def record_wav(path: Path, sample_rate: int = 16000) -> Path:
    """Record from the default microphone until the user presses Enter."""
    import numpy as np
    import sounddevice as sd

    chunks: list[np.ndarray] = []

    def callback(indata, _frames, _time, _status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16", callback=callback):
        input("🎙️  Recording... press Enter to stop. ")

    audio = np.concatenate(chunks) if chunks else np.zeros((0, 1), dtype=np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return path
