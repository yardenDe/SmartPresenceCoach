from unittest.mock import Mock

import numpy as np

import media.audio_extractor as audio_extractor_module
from media.audio_extractor import AudioExtractor


def test_normalize_audio():
    samples = np.array([-32768, 0, 32767], dtype=np.int16)

    result = AudioExtractor._normalize_audio(samples.tobytes())

    expected = samples.astype(np.float32) / audio_extractor_module.PCM_SCALE
    np.testing.assert_allclose(result, expected)


def test_extract(monkeypatch):
    samples = np.array([-1000, 0, 1000], dtype=np.int16)

    run_mock = Mock(
        return_value=Mock(stdout=samples.tobytes())
    )

    monkeypatch.setattr(
        audio_extractor_module.subprocess,
        "run",
        run_mock,
    )

    extractor = AudioExtractor()
    result = extractor.extract("video.mp4")

    expected = samples.astype(np.float32) / audio_extractor_module.PCM_SCALE
    np.testing.assert_allclose(result, expected)

    run_mock.assert_called_once_with(
        extractor._command("video.mp4"),
        stdout=audio_extractor_module.subprocess.PIPE,
        stderr=audio_extractor_module.subprocess.PIPE,
        check=True,
        text=False,
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
        audio_extractor_module.subprocess,
        "Popen",
        popen_mock,
    )

    extractor = AudioExtractor(sample_rate=2)
    chunks = list(extractor.stream("video.mp4", 1))

    assert len(chunks) == 2

    np.testing.assert_allclose(
        chunks[0],
        first.astype(np.float32) / audio_extractor_module.PCM_SCALE,
    )

    np.testing.assert_allclose(
        chunks[1],
        second.astype(np.float32) / audio_extractor_module.PCM_SCALE,
    )

    stdout.read.assert_called_with(
        extractor.sample_rate * extractor.channels * audio_extractor_module.SAMPLE_WIDTH
    )
    process.wait.assert_called_once_with()


def test_custom_audio_settings_are_used():
    extractor = AudioExtractor(
        sample_rate=44100,
        channels=2,
    )

    assert extractor.sample_rate == 44100
    assert extractor.channels == 2

    assert extractor._command("video.mp4")[
        extractor._command("video.mp4").index("-ar") + 1
    ] == "44100"

    assert extractor._command("video.mp4")[
        extractor._command("video.mp4").index("-ac") + 1
    ] == "2"
