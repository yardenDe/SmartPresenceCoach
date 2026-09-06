from collections.abc import Iterator
import io
import subprocess
import wave

import numpy as np

<<<<<<< Updated upstream:backend/app/audio/audio_processor.py
from audio.config import (
=======
from core.exceptions import AudioExtractionError
from core.logger import get_logger
from media.config import (
>>>>>>> Stashed changes:backend/app/media/audio_extractor.py
    BUFFER_SIZE,
    CHANNELS,
    PCM_MAX,
    PCM_SCALE,
    SAMPLE_RATE,
    SAMPLE_WIDTH,
)

logger = get_logger("app.media.audio_extractor")


class AudioProcessor:
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ):
        self.sample_rate = sample_rate
        self.channels = channels

    def _command(self, video_path: str) -> list[str]:
        return [
            "ffmpeg",
            "-i", video_path,
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

    def extract(self, video_path: str) -> np.ndarray:
        try:
            result = subprocess.run(
                self._command(video_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=False,
            )

            return self._normalize_audio(result.stdout)

        except subprocess.CalledProcessError as error:
            stderr = (
                error.stderr.decode("utf-8", errors="replace")
                if error.stderr
                else "No FFmpeg stderr output"
            )
            logger.error(
                "event=audio.extract.failed path=%s error=%s",
                video_path,
                stderr,
            )
            raise AudioExtractionError() from error

<<<<<<< Updated upstream:backend/app/audio/audio_processor.py
        stdout = process.stdout
        if stdout is None:
            process.wait()
            return
=======
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            logger.exception(
                "event=audio.extract.failed path=%s",
                video_path,
            )
            raise AudioExtractionError() from error

    def stream(self, video_path: str) -> Iterator[np.ndarray]:
        process = None
>>>>>>> Stashed changes:backend/app/media/audio_extractor.py

        try:
            process = subprocess.Popen(
                self._command(video_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )

            stdout = process.stdout

            if stdout is None:
                raise AudioExtractionError()

            while True:
                audio_bytes = stdout.read(BUFFER_SIZE)

                if not audio_bytes:
                    break

                yield self._normalize_audio(audio_bytes)
<<<<<<< Updated upstream:backend/app/audio/audio_processor.py
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
=======

            return_code = process.wait()
            if isinstance(return_code, int) and return_code != 0:
                raise AudioExtractionError()

        except AudioExtractionError:
            logger.exception("event=audio.stream.failed path=%s", video_path)
            raise
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            logger.exception("event=audio.stream.failed path=%s", video_path)
            raise AudioExtractionError() from error
        finally:
            if process is not None and process.poll() is None:
                process.wait()
>>>>>>> Stashed changes:backend/app/media/audio_extractor.py
