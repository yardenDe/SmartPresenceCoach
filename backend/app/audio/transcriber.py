import io
import wave

import numpy as np

from media.config import (
    CHANNELS,
    PCM_MAX,
    SAMPLE_RATE,
    SAMPLE_WIDTH,
)


class Transcriber:
    def __init__(
        self,
        client,
        model: str,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ):
        self.client = client
        self.model = model
        self.sample_rate = sample_rate
        self.channels = channels

    def transcribe(
        self,
        audio: np.ndarray,
    ):
        wav_bytes = self._to_wav_bytes(audio)

        response = self.client.audio.transcriptions.create(
            file=("audio.wav", wav_bytes),
            model=self.model,
            response_format="verbose_json",
            timestamp_granularities=[
                "word",
                "segment",
            ],
        )

        return response

    def _to_wav_bytes(
        self,
        audio: np.ndarray,
    ) -> bytes:
        pcm_audio = (
            np.clip(audio, -1.0, 1.0) * PCM_MAX
        ).astype(np.int16)

        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(
                pcm_audio.tobytes()
            )

        return buffer.getvalue()