from unittest.mock import Mock

import numpy as np

from audio.audio_pipeline import AudioPipeline


def test_process_uses_processor_and_engine():
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    rms = np.array([0.15, 0.20], dtype=np.float32)
    pitch = np.array([120.0, 125.0], dtype=np.float32)

    processor = Mock()
    processor.extract.return_value = audio

    engine = Mock()
    engine.rms.return_value = rms
    engine.pitch.return_value = pitch

    pipeline = AudioPipeline(
        processor=processor,
        engine=engine,
    )

    result = pipeline.process()

    processor.extract.assert_called_once_with()
    engine.rms.assert_called_once_with(audio)
    engine.pitch.assert_called_once_with(audio)

    assert result["rms"] is rms
    assert result["pitch"] is pitch
