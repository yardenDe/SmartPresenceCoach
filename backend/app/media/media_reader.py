from dataclasses import dataclass
from collections.abc import Generator
from typing import cast

import av
import numpy as np

from media.config import SAMPLE_RATE, PCM_SCALE


VIDEO_FORMAT = "bgr24"
AUDIO_FORMAT = "s16"
AUDIO_LAYOUT = "mono"


@dataclass(frozen=True)
class VideoSample:
    start_time: float
    end_time: float
    data: np.ndarray


@dataclass(frozen=True)
class AudioSample:
    start_time: float
    end_time: float
    data: np.ndarray


@dataclass
class MediaData:
    start_time: float
    end_time: float
    video: list[VideoSample]
    audio: AudioSample | None


def decode_video_frame(
    frame: av.VideoFrame,
    duration: float = 0.0,
) -> VideoSample:
    start_time = frame.time

    frame_duration = getattr(frame, "duration", None)
    if frame_duration and frame.time_base:
        duration = float(frame_duration * frame.time_base)

    return VideoSample(
        start_time=start_time,
        end_time=start_time + duration,
        data=frame.to_ndarray(format=VIDEO_FORMAT),
    )


def decode_audio_frame(frame: av.AudioFrame) -> AudioSample:
    start_time = frame.time

    return AudioSample(
        start_time=start_time,
        end_time=start_time + frame.samples / frame.sample_rate,
        data=frame.to_ndarray().reshape(-1).astype(np.float32) / PCM_SCALE,
    )


class MediaReader:
    def __init__(self, path: str, target_fps: int | None = None):
        if target_fps is not None and target_fps <= 0:
            raise ValueError("Target FPS must be positive")

        self.path = path
        self.target_fps = target_fps

    def read_iter(
        self,
        video: bool = True,
        audio: bool = True,
    ) -> Generator[VideoSample | AudioSample, None, None]:

        with av.open(self.path) as container:
            streams = []
            resampler = None
            frame_duration = 0.0

            if video and container.streams.video:
                stream = container.streams.video[0]
                streams.append(stream)

                if stream.average_rate:
                    frame_duration = float(1 / stream.average_rate)

            if audio and container.streams.audio:
                streams.append(container.streams.audio[0])

                resampler = av.AudioResampler(
                    format=AUDIO_FORMAT,
                    layout=AUDIO_LAYOUT,
                    rate=SAMPLE_RATE,
                )

            if not streams:
                return

            video_origin = None
            next_sample_time = 0.0

            for frame in container.decode(*streams):
                if isinstance(frame, av.VideoFrame):
                    if self.target_fps is not None and frame.time is not None:
                        if video_origin is None:
                            video_origin = frame.time

                        if frame.time - video_origin < next_sample_time:
                            continue

                        next_sample_time += 1 / self.target_fps

                    yield decode_video_frame(frame, frame_duration)

                elif isinstance(frame, av.AudioFrame) and resampler is not None:
                    for part in resampler.resample(frame):
                        yield decode_audio_frame(part)

            if resampler is not None:
                for part in resampler.resample(None):
                    yield decode_audio_frame(part)

    def read(
        self,
        video: bool = True,
        audio: bool = True,
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
                start_time=audio_chunks[0].start_time,
                end_time=audio_chunks[-1].end_time,
                data=np.concatenate(
                    [sample.data for sample in audio_chunks]
                ),
            )
            if audio_chunks
            else None
        )

        starts = [sample.start_time for sample in video_samples]
        ends = [sample.end_time for sample in video_samples]

        if full_audio is not None:
            starts.append(full_audio.start_time)
            ends.append(full_audio.end_time)

        return MediaData(
            start_time=min(starts) if starts else 0.0,
            end_time=max(ends) if ends else 0.0,
            video=video_samples,
            audio=full_audio,
        )

    def iter_video(self) -> Generator[VideoSample, None, None]:
        for sample in self.read_iter(audio=False):
            if isinstance(sample, VideoSample):
                yield sample

    def iter_audio(self) -> Generator[AudioSample, None, None]:
        for sample in self.read_iter(video=False):
            if isinstance(sample, AudioSample):
                yield sample

    def iter_video_chunks(
        self,
        duration: float,
    ) -> Generator[list[VideoSample], None, None]:

        if duration <= 0:
            raise ValueError("Duration must be positive")

        chunk = []

        for sample in self.iter_video():
            if chunk and sample.start_time - chunk[0].start_time >= duration:
                yield chunk
                chunk = []

            chunk.append(sample)

        if chunk:
            yield chunk

    def iter_audio_chunks(
        self,
        duration: float,
    ) -> Generator[AudioSample, None, None]:

        chunk_size = round(SAMPLE_RATE * duration)

        if chunk_size <= 0:
            raise ValueError("Duration must span at least one audio sample")

        buffer = np.empty(0, dtype=np.float32)
        start_time = None

        for sample in self.iter_audio():
            if start_time is None:
                start_time = sample.start_time

            buffer = np.concatenate((buffer, sample.data))

            while len(buffer) >= chunk_size:
                end_time = start_time + chunk_size / SAMPLE_RATE

                yield AudioSample(
                    start_time=start_time,
                    end_time=end_time,
                    data=buffer[:chunk_size],
                )

                buffer = buffer[chunk_size:]
                start_time = end_time

        if len(buffer):
            yield AudioSample(
                start_time=start_time,
                end_time=start_time + len(buffer) / SAMPLE_RATE,
                data=buffer,
            )
