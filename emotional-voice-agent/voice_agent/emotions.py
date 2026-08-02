"""Emotion vocabulary shared by the LLM brain and the Cartesia TTS layer.

Cartesia's Sonic models take inline SSML-style tags in the transcript:

    <emotion value="angry"/> How dare you speak to me like I'm just a robot!

Tags only help when the emotion is consistent with the words, so the brain
is instructed to pick emotions that match what it is actually saying.
"""

from __future__ import annotations

# Emotions Cartesia documents as giving the strongest, most reliable results.
PRIMARY_EMOTIONS = {
    "neutral",
    "calm",
    "angry",
    "content",
    "sad",
    "scared",
}

# Extended set from Cartesia's emotion list that works well conversationally.
EXTENDED_EMOTIONS = {
    "happy",
    "excited",
    "grateful",
    "curious",
    "surprised",
    "amused",
    "affectionate",
    "sympathetic",
    "apologetic",
    "confident",
    "determined",
    "nostalgic",
    "sarcastic",
    "worried",
    "panicked",
    "disappointed",
    "frustrated",
    "embarrassed",
    "proud",
    "hopeful",
}

SUPPORTED_EMOTIONS = PRIMARY_EMOTIONS | EXTENDED_EMOTIONS

DEFAULT_EMOTION = "neutral"


def normalize_emotion(raw: str | None) -> str:
    """Map an arbitrary emotion label to a supported Cartesia emotion."""
    if not raw:
        return DEFAULT_EMOTION
    emotion = raw.strip().lower()
    if emotion in SUPPORTED_EMOTIONS:
        return emotion
    # Common synonyms the LLM may produce despite instructions.
    synonyms = {
        "joyful": "happy",
        "joy": "happy",
        "cheerful": "happy",
        "enthusiastic": "excited",
        "thrilled": "excited",
        "anxious": "worried",
        "nervous": "worried",
        "afraid": "scared",
        "fearful": "scared",
        "terrified": "panicked",
        "mad": "angry",
        "furious": "angry",
        "annoyed": "frustrated",
        "melancholy": "sad",
        "sorrowful": "sad",
        "thankful": "grateful",
        "loving": "affectionate",
        "warm": "affectionate",
        "empathetic": "sympathetic",
        "compassionate": "sympathetic",
        "sorry": "apologetic",
        "relaxed": "calm",
        "serene": "calm",
        "intrigued": "curious",
        "astonished": "surprised",
        "shocked": "surprised",
    }
    return synonyms.get(emotion, DEFAULT_EMOTION)


def emotion_tag(emotion: str) -> str:
    """Render the inline Cartesia SSML tag for a (already normalized) emotion."""
    return f'<emotion value="{emotion}"/>'
