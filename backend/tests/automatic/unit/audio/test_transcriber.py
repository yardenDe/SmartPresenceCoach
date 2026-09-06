from unittest.mock import Mock
import io
import wave

import numpy as np

from audio.transcriber import Transcriber
from media.config import SAMPLE_WIDTH


def test_to_wav_bytes_creates_valid_wav():
    audio = np.array([-1.0, 0.0, 1.0], dtype=np.float32)

    transcriber = Transcriber(
        client=Mock(),
        model="test-model",
        sample_rate=16000,
        channels=1,
    )

    wav_bytes = transcriber._to_wav_bytes(audio)

    assert isinstance(wav_bytes, bytes)

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getframerate() == 16000
        assert wav_file.getsampwidth() == SAMPLE_WIDTH
        assert wav_file.getnframes() == len(audio)


def test_transcribe_converts_audio_and_calls_client():
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)

    response = Mock()
    create_mock = Mock(return_value=response)

    client = Mock()
    client.audio.transcriptions.create = create_mock

    transcriber = Transcriber(
        client=client,
        model="whisper-large-v3-turbo",
    )

    result = transcriber.transcribe(audio)

    create_mock.assert_called_once()

    call_kwargs = create_mock.call_args.kwargs

    assert call_kwargs["model"] == "whisper-large-v3-turbo"
    assert call_kwargs["response_format"] == "verbose_json"
    assert call_kwargs["timestamp_granularities"] == ["word", "segment"]

    filename, wav_bytes = call_kwargs["file"]
    assert filename == "audio.wav"
    assert isinstance(wav_bytes, bytes)

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == transcriber.channels
        assert wav_file.getframerate() == transcriber.sample_rate
        assert wav_file.getnframes() == len(audio)

    assert result is response


def test_transcriber_keeps_configuration():
    client = Mock()

    transcriber = Transcriber(
        client=client,
        model="test-model",
        sample_rate=44100,
        channels=2,
    )

    assert transcriber.client is client
    assert transcriber.model == "test-model"
    assert transcriber.sample_rate == 44100
    assert transcriber.channels == 2
