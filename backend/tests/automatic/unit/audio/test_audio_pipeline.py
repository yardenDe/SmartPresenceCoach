from unittest.mock import Mock

import numpy as np

from audio.audio_pipeline import AudioPipeline
from schemas.analysis import AudioFeatures


def test_process_combines_librosa_and_transcription():
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)

    rms = np.array([0.11, 0.22], dtype=np.float32)
    pitch = np.array([120.0, 125.0], dtype=np.float32)

    transcription = Mock(text="Hello friends.")

    engine = Mock()
    features = AudioFeatures(
        rms=rms,
        pitch=pitch,
        non_silent_intervals=np.array([[0, 3]]),
        total_samples=3,
    )
    engine.extract_features.return_value = features

    transcriber = Mock()
    transcriber.transcribe.return_value = transcription

    pipeline = AudioPipeline(
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process(audio)

    engine.extract_features.assert_called_once_with(audio)
    transcriber.transcribe.assert_called_once_with(audio)

    assert result.rms is rms
    assert result.pitch is pitch
    assert result.transcript == "Hello friends."


def test_process_returns_only_analysis_results():
    audio = np.array([0.1], dtype=np.float32)

    engine = Mock()
    engine.extract_features.return_value = AudioFeatures(
        rms=np.array([0.1]),
        pitch=np.array([100.0]),
        non_silent_intervals=np.array([[0, 1]]),
        total_samples=1,
    )

    transcriber = Mock()
    transcriber.transcribe.return_value = Mock(text="test")

    pipeline = AudioPipeline(
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process(audio)

    assert isinstance(result, AudioFeatures)
    assert result.transcript == "test"
