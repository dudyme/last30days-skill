from voice_agent.brain import Reply, Segment
from voice_agent.tts import build_transcript


def test_tags_are_interleaved_per_segment():
    reply = Reply(
        segments=[
            Segment(emotion="excited", text="You got the job?!"),
            Segment(emotion="affectionate", text="I'm so proud of you."),
        ]
    )
    assert build_transcript(reply) == (
        '<emotion value="excited"/> You got the job?! '
        '<emotion value="affectionate"/> I\'m so proud of you.'
    )


def test_neutral_segments_carry_no_tag():
    reply = Reply(segments=[Segment(emotion="neutral", text="It opens at nine.")])
    assert build_transcript(reply) == "It opens at nine."


def test_consecutive_same_emotion_tagged_once():
    reply = Reply(
        segments=[
            Segment(emotion="sad", text="I'm sorry to hear that."),
            Segment(emotion="sad", text="That must be hard."),
        ]
    )
    assert build_transcript(reply) == (
        '<emotion value="sad"/> I\'m sorry to hear that. That must be hard.'
    )
