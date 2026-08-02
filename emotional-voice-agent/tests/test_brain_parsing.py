import json

from voice_agent.brain import parse_reply


def test_parses_well_formed_segments():
    raw = json.dumps(
        {
            "segments": [
                {"emotion": "excited", "text": "That's amazing news!"},
                {"emotion": "curious", "text": "How did it happen?"},
            ]
        }
    )
    reply = parse_reply(raw)
    assert [(s.emotion, s.text) for s in reply.segments] == [
        ("excited", "That's amazing news!"),
        ("curious", "How did it happen?"),
    ]
    assert reply.plain_text == "That's amazing news! How did it happen?"


def test_strips_markdown_code_fence():
    raw = '```json\n{"segments": [{"emotion": "sad", "text": "I\'m sorry."}]}\n```'
    reply = parse_reply(raw)
    assert reply.segments[0].emotion == "sad"


def test_unknown_emotion_normalized():
    raw = json.dumps({"segments": [{"emotion": "ecstatic-beyond-words", "text": "Wow!"}]})
    reply = parse_reply(raw)
    assert reply.segments[0].emotion == "neutral"


def test_empty_segments_fall_back_to_raw_text():
    reply = parse_reply('{"segments": []}')
    assert len(reply.segments) == 1
    assert reply.segments[0].emotion == "neutral"


def test_non_json_falls_back_to_neutral_speech():
    reply = parse_reply("Sure, happy to help with that!")
    assert reply.segments == reply.segments  # parse must not raise
    assert reply.segments[0].text == "Sure, happy to help with that!"
    assert reply.segments[0].emotion == "neutral"


def test_segments_with_blank_text_are_dropped():
    raw = json.dumps(
        {
            "segments": [
                {"emotion": "happy", "text": "   "},
                {"emotion": "calm", "text": "Take a breath."},
            ]
        }
    )
    reply = parse_reply(raw)
    assert [(s.emotion, s.text) for s in reply.segments] == [("calm", "Take a breath.")]
