
from dataclasses import dataclass
from collections.abc import Generator
from itertools import chain

import av
import numpy as np

from core.logger import get_logger
from media.config import (
    AUDIO_FORMAT,
    AUDIO_LAYOUT,
    AUDIO_TIMESTAMP_TOLERANCE,
    PCM_SCALE,
    SAMPLE_RATE,
    TARGET_FPS,
    VIDEO_CHUNK_DURATION_SECONDS,
    VIDEO_FORMAT,
)

logger = get_logger("app.media.reader")


@dataclass(frozen=True)
class Video:
    start_time: float
    end_time: float
    frames: list[np.ndarray]


@dataclass(frozen=True)
class Audio:
    start_time: float
    end_time: float
    data: np.ndarray


class MediaReader:
    def __init__(self, path: str):
        self.path = path

    def read_iter(
        self,
        video: bool = True,
        audio: bool = True,
    ) -> Generator[av.VideoFrame | av.AudioFrame, None, None]:

        logger.debug("event=media.read.start video=%s audio=%s", video, audio)
        with av.open(self.path) as container:
            streams = []

            if video and container.streams.video:
                streams.append(container.streams.video[0])

            if audio and container.streams.audio:
                streams.append(container.streams.audio[0])

            if not streams:
                logger.debug("event=media.read.empty video=%s audio=%s", video, audio)
                return

            logger.debug("event=media.streams.selected count=%s", len(streams))
            for frame in container.decode(*streams):
                yield frame

        logger.debug("event=media.read.done video=%s audio=%s", video, audio)

    def iter_video_chunks(
        self,
        duration: float = VIDEO_CHUNK_DURATION_SECONDS,
        target_fps: int = TARGET_FPS
    ) -> Generator[Video, None, None]:

        logger.debug("event=media.video.start duration=%s target_fps=%s", duration, target_fps)
        frames = []
        start_time = 0
        end_time = start_time + duration
        sample_time = 1 / target_fps
        step = sample_time
        last_time = 0

        for frame in self.read_iter(audio=False):
            timestamp = frame.time
            last_time = timestamp

            if timestamp >= end_time:
                yield Video(start_time, end_time, frames)
                frames = []
                start_time = end_time
                end_time = start_time + duration

            if timestamp >= step:
                frames.append(frame.to_ndarray(format=VIDEO_FORMAT))
                step += sample_time

        if frames:
            logger.debug(
                "event=media.video.chunk start_time=%.3f end_time=%.3f last_time=%s selected=%s",
                start_time, end_time, last_time, len(frames),
            )
            yield Video(start_time, last_time, frames)

    
    def read_audio(self) -> list[Audio]:
        logger.debug("event=media.audio.start sample_rate=%s", SAMPLE_RATE)

        resampler = av.AudioResampler(
            format=AUDIO_FORMAT,
            layout=AUDIO_LAYOUT,
            rate=SAMPLE_RATE
        )

        chunks = []

        for frame in chain(self.read_iter(video=False), [None]):
            for part in resampler.resample(frame):
                chunks.append(
                    part.to_ndarray().reshape(-1).astype(np.float32) / PCM_SCALE
                )

        if not chunks:
            return []

        data = np.concatenate(chunks)
        end_time = len(data) / SAMPLE_RATE

        logger.debug(
            "event=media.audio.done segments=1 samples=%s",
            len(data),
        )

        return [Audio(0, end_time, data)]

