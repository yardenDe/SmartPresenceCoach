from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from analytics.audio.audio_analytics_manager import AudioAnalyticsManager
from analytics.config import ANALYSIS_WINDOW_SECONDS
from analytics.config import AudioMetrics, Snapshot, VideoMetrics
from db.models.analysis import AnalysisRecord, AudioFeatureRecord, AudioMetric, Transcript, VideoMetric
from extraction.audio.config import AudioFeatures


@dataclass(frozen=True)
class TimelineEntry:
    start_time: float
    end_time: float
    video: VideoMetrics | None = None
    audio: AudioMetrics | None = None
    transcript: str | None = None


class TimelineBuilder:
    def build_from_records(
        self,
        session_id: int,
        records: Iterable[AnalysisRecord],
    ) -> list[Snapshot]:
        entries = []
        for record in records:
            if isinstance(record, AudioFeatureRecord):
                entries.extend(self._audio_entries(record))
            elif isinstance(record, VideoMetric):
                entries.append(TimelineEntry(
                    record.start_time, record.end_time,
                    video=VideoMetrics.model_validate(record, from_attributes=True),
                ))
            elif isinstance(record, AudioMetric):
                entries.append(TimelineEntry(
                    record.start_time, record.end_time,
                    audio=AudioMetrics.model_validate(record, from_attributes=True),
                ))
            elif isinstance(record, Transcript):
                entries.append(TimelineEntry(
                    record.start_time, record.end_time,
                    transcript=record.transcript,
                ))
        return self.build(session_id, entries)

    @staticmethod
    def _audio_entries(record: AudioFeatureRecord) -> list[TimelineEntry]:
        entries = []
        sample_rate = record.sample_rate
        duration = record.total_samples / sample_rate
        analytics = AudioAnalyticsManager()
        intervals = np.asarray(record.non_silent_intervals, dtype=int).reshape(-1, 2)

        start = 0.0
        while start < duration:
            end = min(start + ANALYSIS_WINDOW_SECONDS, duration)
            first_sample = round(start * sample_rate)
            last_sample = min(round(end * sample_rate), record.total_samples)
            first_frame = round(first_sample / record.hop_length)
            last_frame = round(last_sample / record.hop_length)

            clipped = np.column_stack((
                np.maximum(intervals[:, 0], first_sample) - first_sample,
                np.minimum(intervals[:, 1], last_sample) - first_sample,
            ))
            clipped = clipped[clipped[:, 1] > clipped[:, 0]]

            features = AudioFeatures(
                rms=np.asarray(record.rms[first_frame:last_frame], dtype=float),
                pitch=np.asarray(record.pitch[first_frame:last_frame], dtype=float),
                non_silent_intervals=clipped,
                total_samples=last_sample - first_sample,
                sample_rate=sample_rate,
                hop_length=record.hop_length,
            )
            entries.append(TimelineEntry(
                start_time=record.start_time + start,
                end_time=min(record.start_time + end, record.end_time),
                audio=analytics.analyze(features),
            ))
            start = end

        return entries

    @staticmethod
    def build(session_id: int, entries: Iterable[TimelineEntry]) -> list[Snapshot]:
        entries = list(entries)
        times = sorted({t for entry in entries for t in (entry.start_time, entry.end_time)})
        snapshots = []

        for start, end in zip(times, times[1:]):
            video = audio = transcript = None
            for entry in entries:
                if entry.start_time < end and entry.end_time > start:
                    if entry.video is not None:
                        video = entry.video
                    if entry.audio is not None:
                        audio = entry.audio
                    if entry.transcript is not None and entry.start_time == start:
                        transcript = entry.transcript

            if video is not None or audio is not None or transcript is not None:
                snapshots.append(Snapshot(session_id, start, end, video, audio, transcript))

        return snapshots
