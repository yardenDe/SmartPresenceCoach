
from dataclasses import dataclass
from collections.abc import Iterator
from itertools import islice

import av
import numpy as np

from media.config import SAMPLE_RATE, PCM_SCALE


@dataclass(frozen=True)
class VideoSample:
    timestamp: float
    data: np.ndarray


@dataclass(frozen=True)
class AudioSample:
    timestamp: float
    data: np.ndarray


@dataclass
class MediaData:
    video: list[VideoSample]
    audio: AudioSample | None


def decode_video_frame(frame: av.VideoFrame) -> VideoSample:
    return VideoSample(
        timestamp=float(frame.time or 0.0),
        data=frame.to_ndarray(format="bgr24")
    )


def decode_audio_frame(frame: av.AudioFrame) -> AudioSample:
    return AudioSample(
        timestamp=float(frame.time or 0.0),
        data=frame.to_ndarray().reshape(-1).astype(np.float32) / PCM_SCALE
    )


class MediaReader:
    def __init__(self, path: str):
        self.path = path

    def read_iter(
        self, video: bool = True, audio: bool = True
    ) -> Iterator[VideoSample | AudioSample]:

        with av.open(self.path) as container:
            streams = []

            if video and container.streams.video:
                streams.append(container.streams.video[0])

            if audio and container.streams.audio:
                streams.append(container.streams.audio[0])

            if not streams:
                return

            resampler = (
                av.AudioResampler(
                    format="s16",
                    layout="mono",
                    rate=SAMPLE_RATE
                )
                if audio and container.streams.audio
                else None
            )

            for frame in container.decode(*streams):
                if isinstance(frame, av.VideoFrame):
                    yield decode_video_frame(frame)

                elif isinstance(frame, av.AudioFrame):
                    for part in resampler.resample(frame):
                        yield decode_audio_frame(part)

            if resampler is not None:
                for part in resampler.resample(None):
                    yield decode_audio_frame(part)

    def read(
        self, video: bool = True, audio: bool = True
    ) -> MediaData:

        video_samples = []
        audio_chunks = []

        for sample in self.read_iter(video, audio):
            if isinstance(sample, VideoSample):
                video_samples.append(sample)
            else:
                audio_chunks.append(sample)

        full_audio = (
            AudioSample(
                timestamp=audio_chunks[0].timestamp,
                data=np.concatenate(
                    [sample.data for sample in audio_chunks]
                )
            )
            if audio_chunks else None
        )

        return MediaData(
            video=video_samples,
            audio=full_audio
        )

    def read_video(self) -> list[VideoSample]:
        return self.read(video=True, audio=False).video

    def read_audio(self) -> AudioSample | None:
        return self.read(video=False, audio=True).audio

    def iter_video(self) -> Iterator[VideoSample]:
        return self.read_iter(video=True, audio=False)

    def iter_audio(self) -> Iterator[AudioSample]:
        return self.read_iter(video=False, audio=True)

    def iter_video_chunks(
        self, size: int
    ) -> Iterator[list[VideoSample]]:

        if size <= 0:
            raise ValueError("Chunk size must be positive")

        iterator = self.iter_video()

        while chunk := list(islice(iterator, size)):
            yield chunk

    def iter_audio_chunks(
        self, duration: float
    ) -> Iterator[AudioSample]:

        if duration <= 0:
            raise ValueError("Duration must be positive")

        chunk_size = round(SAMPLE_RATE * duration)
        buffer = np.empty(0, dtype=np.float32)
        start_time = None

        for sample in self.iter_audio():
            if start_time is None:
                start_time = sample.timestamp

            buffer = np.concatenate((buffer, sample.data))

            while len(buffer) >= chunk_size:
                yield AudioSample(
                    timestamp=start_time,
                    data=buffer[:chunk_size]
                )

                buffer = buffer[chunk_size:]
                start_time += duration

        if len(buffer):
            yield AudioSample(
                timestamp=start_time,
                data=buffer
            )
