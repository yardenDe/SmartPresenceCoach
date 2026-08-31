from unittest.mock import Mock

import numpy as np

from audio.audio_pipeline import AudioPipeline


def test_process_combines_librosa_and_transcription():
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)

    rms = np.array([0.11, 0.22], dtype=np.float32)
    pitch = np.array([120.0, 125.0], dtype=np.float32)

    words = [
        {"word": "Hello", "start": 0.1, "end": 0.34},
        {"word": "friends.", "start": 0.34, "end": 1.14},
    ]

    segments = [
        {
            "start": 0.0,
            "end": 0.84,
            "text": "Hello friends.",
        }
    ]

    transcription = Mock(
        text="Hello friends.",
        words=words,
        segments=segments,
    )

    engine = Mock()
    engine.rms.return_value = rms
    engine.pitch.return_value = pitch

    transcriber = Mock()
    transcriber.transcribe.return_value = transcription

    pipeline = AudioPipeline(
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process(audio)

    engine.rms.assert_called_once_with(audio)
    engine.pitch.assert_called_once_with(audio)
    transcriber.transcribe.assert_called_once_with(audio)

    assert result["rms"] is rms
    assert result["pitch"] is pitch
    assert result["text"] == "Hello friends."
    assert result["words"] == words
    assert result["segments"] == segments


def test_process_returns_only_analysis_results():
    audio = np.array([0.1], dtype=np.float32)

    engine = Mock()
    engine.rms.return_value = np.array([0.1])
    engine.pitch.return_value = np.array([100.0])

    transcriber = Mock()
    transcriber.transcribe.return_value = Mock(
        text="test",
        words=[],
        segments=[],
    )

    pipeline = AudioPipeline(
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process(audio)

    assert set(result) == {
        "rms",
        "pitch",
        "text",
        "words",
        "segments",
    }
