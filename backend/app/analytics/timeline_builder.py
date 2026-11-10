from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from models.snapshot import Snapshot


@dataclass(frozen=True)
class TimelineEntry:
    start_time: float
    end_time: float
    values: Mapping


class TimelineBuilder:
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
