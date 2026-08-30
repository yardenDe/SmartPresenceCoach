from collections.abc import Iterator
import io
import subprocess
import wave

import numpy as np

from audio.config import (
    BUFFER_SIZE,
    CHANNELS,
    PCM_MAX,
    PCM_SCALE,
    SAMPLE_RATE,
    SAMPLE_WIDTH,
)


class AudioProcessor:
    def __init__(
        self,
        video_path: str,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ):
        self.video_path = video_path
        self.sample_rate = sample_rate
        self.channels = channels

        self.command = [
            "ffmpeg",
            "-i", self.video_path,
            "-vn",
            "-ac", str(self.channels),
            "-ar", str(self.sample_rate),
            "-f", "s16le",
            "pipe:1",
        ]

    @staticmethod
    def _normalize_audio(audio_bytes: bytes) -> np.ndarray:
        audio = np.frombuffer(
            audio_bytes,
            dtype=np.int16,
        ).astype(np.float32)

        return audio / PCM_SCALE

    def extract(self) -> np.ndarray:
        result = subprocess.run(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        return self._normalize_audio(result.stdout)

    def stream(self) -> Iterator[np.ndarray]:
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        stdout = process.stdout
        if stdout is None:
            process.wait()
            return

        try:
            while True:
                audio_bytes = stdout.read(BUFFER_SIZE)

                if not audio_bytes:
                    break

                yield self._normalize_audio(audio_bytes)
        finally:
            process.wait()

    def to_wav_bytes(self, audio: np.ndarray) -> bytes:
        pcm_audio = (
            np.clip(audio, -1.0, 1.0) * PCM_MAX
        ).astype(np.int16)

        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_audio.tobytes())

        return buffer.getvalue()
