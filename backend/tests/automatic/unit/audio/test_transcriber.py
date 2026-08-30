from unittest.mock import Mock

from audio.transcriber import Transcriber


def test_transcribe_calls_client_and_returns_response():
    wav_bytes = b"fake-wav-bytes"

    response = Mock()
    create_mock = Mock(return_value=response)

    client = Mock()
    client.audio.transcriptions.create = create_mock

    transcriber = Transcriber(
        client=client,
        model="whisper-large-v3-turbo",
    )

    result = transcriber.transcribe(wav_bytes)

    create_mock.assert_called_once_with(
        file=("audio.wav", wav_bytes),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"],
    )

    assert result is response


def test_transcriber_keeps_client_and_model():
    client = Mock()

    transcriber = Transcriber(
        client=client,
        model="test-model",
    )

    assert transcriber.client is client
    assert transcriber.model == "test-model"
