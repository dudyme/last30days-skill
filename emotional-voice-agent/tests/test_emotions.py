from voice_agent.emotions import (
    DEFAULT_EMOTION,
    SUPPORTED_EMOTIONS,
    emotion_tag,
    normalize_emotion,
)


def test_supported_emotions_pass_through():
    for emotion in SUPPORTED_EMOTIONS:
        assert normalize_emotion(emotion) == emotion


def test_case_and_whitespace_are_normalized():
    assert normalize_emotion("  Excited ") == "excited"
    assert normalize_emotion("ANGRY") == "angry"


def test_synonyms_map_to_supported_emotions():
    assert normalize_emotion("joyful") == "happy"
    assert normalize_emotion("anxious") == "worried"
    assert normalize_emotion("furious") == "angry"
    assert normalize_emotion("terrified") == "panicked"


def test_unknown_and_empty_fall_back_to_neutral():
    assert normalize_emotion("bamboozled") == DEFAULT_EMOTION
    assert normalize_emotion("") == DEFAULT_EMOTION
    assert normalize_emotion(None) == DEFAULT_EMOTION


def test_emotion_tag_format():
    assert emotion_tag("excited") == '<emotion value="excited"/>'
