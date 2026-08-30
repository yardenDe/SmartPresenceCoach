from unittest.mock import Mock
import io
import wave

import numpy as np

import audio.audio_processor as audio_processor_module
from audio.audio_processor import AudioProcessor


def test_normalize_audio():
    samples = np.array([-32768, 0, 32767], dtype=np.int16)

    result = AudioProcessor._normalize_audio(samples.tobytes())

    expected = samples.astype(np.float32) / audio_processor_module.PCM_SCALE
    np.testing.assert_allclose(result, expected)


def test_extract(monkeypatch):
    samples = np.array([-1000, 0, 1000], dtype=np.int16)

    run_mock = Mock(
        return_value=Mock(stdout=samples.tobytes())
    )
    monkeypatch.setattr(
        audio_processor_module.subprocess,
        "run",
        run_mock,
    )

    processor = AudioProcessor("video.mp4")
    result = processor.extract()

    expected = samples.astype(np.float32) / audio_processor_module.PCM_SCALE
    np.testing.assert_allclose(result, expected)

    run_mock.assert_called_once_with(
        processor.command,
        stdout=audio_processor_module.subprocess.PIPE,
        stderr=audio_processor_module.subprocess.DEVNULL,
        check=True,
    )


def test_stream(monkeypatch):
    first = np.array([100, 200], dtype=np.int16)
    second = np.array([300, 400], dtype=np.int16)

    stdout = Mock()
    stdout.read.side_effect = [
        first.tobytes(),
        second.tobytes(),
        b"",
    ]

    process = Mock()
    process.stdout = stdout

    popen_mock = Mock(return_value=process)
    monkeypatch.setattr(
        audio_processor_module.subprocess,
        "Popen",
        popen_mock,
    )

    processor = AudioProcessor("video.mp4")
    chunks = list(processor.stream())

    assert len(chunks) == 2

    np.testing.assert_allclose(
        chunks[0],
        first.astype(np.float32) / audio_processor_module.PCM_SCALE,
    )
    np.testing.assert_allclose(
        chunks[1],
        second.astype(np.float32) / audio_processor_module.PCM_SCALE,
    )

    stdout.read.assert_called_with(audio_processor_module.BUFFER_SIZE)
    process.wait.assert_called_once_with()


def test_to_wav_bytes():
    audio = np.array([-1.0, 0.0, 1.0], dtype=np.float32)
    processor = AudioProcessor("video.mp4")

    wav_bytes = processor.to_wav_bytes(audio)

    assert isinstance(wav_bytes, bytes)

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        assert wav_file.getnchannels() == processor.channels
        assert wav_file.getframerate() == processor.sample_rate
        assert wav_file.getsampwidth() == audio_processor_module.SAMPLE_WIDTH
        assert wav_file.getnframes() == len(audio)


def test_custom_audio_settings_are_used():
    processor = AudioProcessor(
        "video.mp4",
        sample_rate=44100,
        channels=2,
    )

    assert processor.sample_rate == 44100
    assert processor.channels == 2

    assert processor.command[
        processor.command.index("-ar") + 1
    ] == "44100"

    assert processor.command[
        processor.command.index("-ac") + 1
    ] == "2"
