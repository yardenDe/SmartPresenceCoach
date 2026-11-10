from collections.abc import Iterable, Mapping
from dataclasses import dataclass

import numpy as np

from analytics.audio.manager import AudioAnalyticsManager
from db.models.analysis import AudioFeatureRecord, AudioMetric, Transcript, VideoMetric
from db.models.snapshot import Snapshot
from media.config import SAMPLE_RATE
from schemas.analysis import AudioFeatures

RECORD_FIELDS = {
    VideoMetric: (
        "face_direction", "movement_amount", "movement_variation",
        "head_movement", "shoulder_tilt", "hand_movement",
    ),
    AudioMetric: (
        "pause_ratio", "average_volume", "volume_variation", "pitch_variation",
    ),
    Transcript: ("transcript",),
}


@dataclass(frozen=True)
class TimelineEntry:
    start_time: float
    end_time: float
    values: Mapping


class TimelineBuilder:
    def build_from_records(
        self,
        session_id: int,
        records: Iterable[VideoMetric | AudioMetric | Transcript | AudioFeatureRecord],
    ) -> list[Snapshot]:
        entries = []
        for record in records:
            if isinstance(record, AudioFeatureRecord):
                entries.extend(self._audio_entries(record))
            else:
                values = {name: getattr(record, name) for name in RECORD_FIELDS[type(record)]}
                entries.append(TimelineEntry(record.start_time, record.end_time, values))
        return self.build(session_id, [entries])

    @staticmethod
    def _audio_entries(record: AudioFeatureRecord) -> list[TimelineEntry]:
        audio_entries = []
        duration = record.total_samples / SAMPLE_RATE
        if duration <= 0:
            return audio_entries
        window_start = 0.0
        while window_start < duration:
            window_end = min(window_start + 3.0, duration)
            start_sample = round(window_start * SAMPLE_RATE)
            end_sample = min(round(window_end * SAMPLE_RATE), record.total_samples)
            first_frame = round(start_sample / record.hop_length)
            last_frame = round(end_sample / record.hop_length)
            intervals = np.asarray(record.non_silent_intervals, dtype=int).reshape(-1, 2)
            clipped = np.column_stack((
                np.maximum(intervals[:, 0], start_sample) - start_sample,
                np.minimum(intervals[:, 1], end_sample) - start_sample,
            ))
            clipped = clipped[clipped[:, 1] > clipped[:, 0]]
            features = AudioFeatures(
                rms=np.asarray(record.rms[first_frame:last_frame], dtype=float),
                pitch=np.asarray(record.pitch[first_frame:last_frame], dtype=float),
                non_silent_intervals=clipped,
                total_samples=end_sample - start_sample,
            )
            metrics = AudioAnalyticsManager().analyze(features)
            audio_entries.append(TimelineEntry(
                record.start_time + window_start,
                min(record.start_time + window_end, record.end_time),
                metrics.model_dump(),
            ))
            window_start = window_end
        return audio_entries

    def build(
        self, session_id: int, streams: Iterable[Iterable[TimelineEntry]]
    ) -> list[Snapshot]:
        entries = [entry for stream in streams for entry in stream]
        times = sorted({time for entry in entries for time in (entry.start_time, entry.end_time)})
        snapshots = []

        for start, end in zip(times, times[1:]):
            values = {}
            for entry in entries:
                if entry.start_time < end and entry.end_time > start:
                    for name, value in entry.values.items():
                        if name != "transcript" or entry.start_time == start:
                            values[name] = value

            if values:
                snapshots.append(Snapshot(session_id, start, end_time=end, **values))

        return snapshots
