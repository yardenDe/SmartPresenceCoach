from unittest.mock import Mock

import numpy as np

from audio.audio_pipeline import AudioPipeline
from schemas.analysis import AudioFeatures


def test_process_combines_audio_processing_librosa_and_transcription():
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    wav_bytes = b"wav-bytes"

    rms = np.array([0.11, 0.22], dtype=np.float32)
    pitch = np.array([120.0, 125.0], dtype=np.float32)

    transcription = Mock(text="Hello friends.")

    processor = Mock()
    processor.extract.return_value = audio
    processor.to_wav_bytes.return_value = wav_bytes

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
        processor=processor,
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process()

    processor.extract.assert_called_once_with()
    processor.to_wav_bytes.assert_called_once_with(audio)

<<<<<<< Updated upstream
    engine.rms.assert_called_once_with(audio)
    engine.pitch.assert_called_once_with(audio)

    transcriber.transcribe.assert_called_once_with(wav_bytes)
=======
    engine.extract_features.assert_called_once_with(audio)
    transcriber.transcribe.assert_called_once_with(audio)
>>>>>>> Stashed changes

    assert result.rms is rms
    assert result.pitch is pitch
    assert result.transcript == "Hello friends."


def test_process_returns_only_analysis_results():
    processor = Mock()
    processor.extract.return_value = np.array([0.1], dtype=np.float32)
    processor.to_wav_bytes.return_value = b"wav"

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
        processor=processor,
        engine=engine,
        transcriber=transcriber,
    )

    result = pipeline.process()

    assert isinstance(result, AudioFeatures)
    assert result.transcript == "test"
