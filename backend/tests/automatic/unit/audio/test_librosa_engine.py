from unittest.mock import Mock

import numpy as np

import audio.librosa_engine as librosa_engine_module
from audio.librosa_engine import LibrosaEngine


def test_rms(monkeypatch):
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    librosa_result = np.array([[0.2, 0.3]], dtype=np.float32)

    rms_mock = Mock(return_value=librosa_result)
    monkeypatch.setattr(
        librosa_engine_module.librosa.feature,
        "rms",
        rms_mock,
    )

    engine = LibrosaEngine()
    result = engine.rms(audio)

    np.testing.assert_array_equal(result, librosa_result[0])
    rms_mock.assert_called_once_with(y=audio)


def test_pitch(monkeypatch):
    audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    expected = np.array([120.0, 125.0], dtype=np.float32)

    note_to_hz_mock = Mock(side_effect=[65.0, 2093.0])
    yin_mock = Mock(return_value=expected)

    monkeypatch.setattr(
        librosa_engine_module.librosa,
        "note_to_hz",
        note_to_hz_mock,
    )
    monkeypatch.setattr(
        librosa_engine_module.librosa,
        "yin",
        yin_mock,
    )

    engine = LibrosaEngine(sample_rate=16000)
    result = engine.pitch(audio)

    np.testing.assert_array_equal(result, expected)

    assert note_to_hz_mock.call_args_list[0].args == ("C2",)
    assert note_to_hz_mock.call_args_list[1].args == ("C7",)

    yin_mock.assert_called_once_with(
        audio,
        fmin=65.0,
        fmax=2093.0,
        sr=16000,
    )


def test_custom_sample_rate():
    engine = LibrosaEngine(sample_rate=44100)

    assert engine.sample_rate == 44100


def test_extract_features(monkeypatch):
    audio = np.array([0.1, 0.0, 0.2], dtype=np.float32)
    rms = np.array([0.1, 0.2], dtype=np.float32)
    pitch = np.array([120.0, 125.0], dtype=np.float32)
    intervals = np.array([[0, 1], [2, 3]])
    engine = LibrosaEngine()

    monkeypatch.setattr(engine, "rms", Mock(return_value=rms))
    monkeypatch.setattr(engine, "pitch", Mock(return_value=pitch))
    monkeypatch.setattr(
        engine,
        "non_silent_intervals",
        Mock(return_value=intervals),
    )

    result = engine.extract_features(audio)

    assert result.rms is rms
    assert result.pitch is pitch
    assert result.non_silent_intervals is intervals
    assert result.total_samples == 3
