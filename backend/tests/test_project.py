"""
Updated unit-focused test suite for SmartPresenceCoach.

Run locally from backend/:
    pytest tests/test_project_new.py -v

Run one class/test:
    pytest tests/test_project_new.py::TestAnalyticsManager -v
    pytest tests/test_project_new.py::TestOfflineService::test_process_success -v

Docker (after pytest is installed in the backend image and tests are mounted/copied):
    docker compose run --rm backend pytest tests/test_project_new.py -v

This file intentionally does NOT run the real MediaPipe models. Those belong in a
separate integration test because they depend on native libraries/model files.
"""

from __future__ import annotations

import os
import sys
import types
from enum import Enum
from pathlib import Path
from unittest.mock import Mock

import pytest


# -----------------------------------------------------------------------------
# Make backend/app importable both on the host and in the container.
# -----------------------------------------------------------------------------
PROJECT_OR_CONTAINER_DIR = Path(__file__).resolve().parents[1]
HOST_APP_DIR = PROJECT_OR_CONTAINER_DIR / "app"
APP_DIR = HOST_APP_DIR if HOST_APP_DIR.exists() else PROJECT_OR_CONTAINER_DIR

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Required by core.config/db imports during unit tests; no real DB connection is opened.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("MEDIAPIPE_RUNNING_MODE", "IMAGE")


# -----------------------------------------------------------------------------
# Unit tests should not import/initialize real MediaPipe.
# SessionAnalysisService and VisionPipeline only need the detector TYPE here.
# -----------------------------------------------------------------------------
class DummyMediaPipeDetector:
    pass


# core.config imports RunningMode even in tests. Provide only the tiny piece it needs.
class DummyRunningMode(str, Enum):
    IMAGE = "IMAGE"


mediapipe_module = types.ModuleType("mediapipe")
tasks_module = types.ModuleType("mediapipe.tasks")
python_module = types.ModuleType("mediapipe.tasks.python")
vision_module = types.ModuleType("mediapipe.tasks.python.vision")
vision_module.RunningMode = DummyRunningMode

sys.modules.setdefault("mediapipe", mediapipe_module)
sys.modules.setdefault("mediapipe.tasks", tasks_module)
sys.modules.setdefault("mediapipe.tasks.python", python_module)
sys.modules.setdefault("mediapipe.tasks.python.vision", vision_module)

sys.modules["vision.mediapipe_detector"] = types.SimpleNamespace(
    MediaPipeDetector=DummyMediaPipeDetector
)


# -----------------------------------------------------------------------------
# Shared fake landmark data. This is the contract Analytics receives AFTER
# LandmarkExtractor, so analytics can be tested without running a video pipeline.
# -----------------------------------------------------------------------------
def sample_frame(offset: float = 0.0) -> dict:
    return {
        "pose": {
            "nose": {"x": 0.50 + offset, "y": 0.20},
            "left_ear": {"x": 0.38 + offset, "y": 0.22},
            "right_ear": {"x": 0.62 + offset, "y": 0.22},
            "left_shoulder": {"x": 0.35 + offset, "y": 0.40},
            "right_shoulder": {"x": 0.65 + offset, "y": 0.40},
            "left_elbow": {"x": 0.25 + offset, "y": 0.55},
            "right_elbow": {"x": 0.75 + offset, "y": 0.55},
            "left_wrist_basic": {"x": 0.22 + offset, "y": 0.66},
            "right_wrist_basic": {"x": 0.78 + offset, "y": 0.66},
            "left_hip": {"x": 0.42 + offset, "y": 0.72},
            "right_hip": {"x": 0.58 + offset, "y": 0.72},
        },
        "face": {
            "left_iris_center": {"x": 0.46 + offset, "y": 0.24},
            "right_iris_center": {"x": 0.54 + offset, "y": 0.24},
            "left_eye_outer": {"x": 0.44 + offset, "y": 0.24},
            "left_eye_inner": {"x": 0.48 + offset, "y": 0.24},
            "right_eye_inner": {"x": 0.52 + offset, "y": 0.24},
            "right_eye_outer": {"x": 0.56 + offset, "y": 0.24},
            "mouth_top": {"x": 0.50 + offset, "y": 0.34},
            "mouth_bottom": {"x": 0.50 + offset, "y": 0.37 + offset},
            "forehead": {"x": 0.50 + offset, "y": 0.14},
            "chin": {"x": 0.50 + offset, "y": 0.43},
            "left_cheek": {"x": 0.40 + offset, "y": 0.29},
            "right_cheek": {"x": 0.60 + offset, "y": 0.29},
        },
        "hands": [
            {
                "label": "Left",
                "points": {
                    "hand_wrist": {"x": 0.32 + offset, "y": 0.65},
                    "hand_thumb_tip": {"x": 0.29 + offset, "y": 0.58},
                    "hand_index_tip": {"x": 0.30 + offset, "y": 0.55},
                    "hand_middle_tip": {"x": 0.31 + offset, "y": 0.54},
                    "hand_ring_tip": {"x": 0.32 + offset, "y": 0.55},
                    "hand_pinky_tip": {"x": 0.33 + offset, "y": 0.57},
                },
            },
            {
                "label": "Right",
                "points": {
                    "hand_wrist": {"x": 0.68 + offset, "y": 0.65},
                    "hand_thumb_tip": {"x": 0.71 + offset, "y": 0.58},
                    "hand_index_tip": {"x": 0.70 + offset, "y": 0.55},
                    "hand_middle_tip": {"x": 0.69 + offset, "y": 0.54},
                    "hand_ring_tip": {"x": 0.68 + offset, "y": 0.55},
                    "hand_pinky_tip": {"x": 0.67 + offset, "y": 0.57},
                },
            },
        ],
    }


class TestAnalyticsMath:
    def test_score_helpers(self):
        from analytics import math_utils as math

        assert math.clamp(120) == 100.0
        assert math.clamp(-20) == 0.0
        assert math.clamp_score(55.678) == 55.68
        assert math.average([10, 20, 30]) == 20
        assert math.average([]) == 0.0
        assert math.weighted_average([(80, 0.75), (40, 0.25)]) == 70

    def test_point_helpers(self):
        from analytics import math_utils as math

        a = {"x": 0.1, "y": 0.2}
        b = {"x": 0.4, "y": 0.6}

        assert math.point_distance(a, b) == pytest.approx(0.5)
        assert math.axis_distance(a, b, "x") == pytest.approx(0.3)
        assert math.midpoint(a, b) == pytest.approx({"x": 0.25, "y": 0.4})
        assert math.average_absolute_change([1.0, 3.0, 2.0]) == pytest.approx(1.5)


class TestMetricAnalyzers:
    def test_every_analyzer_returns_score_in_range(self):
        from analytics.metrics.composure_analyzer import ComposureAnalyzer
        from analytics.metrics.engagement_analyzer import EngagementAnalyzer
        from analytics.metrics.focus_analyzer import FocusAnalyzer
        from analytics.metrics.posture_analyzer import PostureAnalyzer
        from analytics.metrics.presence_analyzer import PresenceAnalyzer

        frames = [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
        analyzers = [
            FocusAnalyzer(),
            PostureAnalyzer(),
            EngagementAnalyzer(),
            PresenceAnalyzer(),
            ComposureAnalyzer(),
        ]

        for analyzer in analyzers:
            score = analyzer.analyze(frames)
            assert score is not None, analyzer.__class__.__name__
            assert 0 <= score <= 100, analyzer.__class__.__name__


class TestAnalyticsManager:
    def test_run_full_analysis_returns_metrics_and_overall(self):
        from analytics.manager import AnalyticsManager

        result = AnalyticsManager().run_full_analysis(
            [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
        )

        assert set(result) == {
            "focus",
            "posture",
            "engagement",
            "presence",
            "composure",
            "overall",
        }

        for score in result.values():
            assert isinstance(score, (int, float))
            assert 0 <= score <= 100

        metric_values = [
            result["focus"],
            result["posture"],
            result["engagement"],
            result["presence"],
            result["composure"],
        ]
        assert result["overall"] == pytest.approx(sum(metric_values) / len(metric_values))

    def test_empty_input_raises_analytics_error(self):
        from analytics.manager import AnalyticsManager
        from core.exceptions import AnalyticsProcessingError

        with pytest.raises(AnalyticsProcessingError):
            AnalyticsManager().run_full_analysis([])


class TestSessionBuffer:
    def test_add_flush_and_close(self):
        from services.session_buffer import SessionBuffer

        buffer = SessionBuffer(flush_size=2)

        buffer.add(10, {"overall": 80, "timestamp": 0.0})
        assert buffer.should_flush(10) is False

        buffer.add(10, {"overall": 90, "timestamp": 3.0})
        assert buffer.should_flush(10) is True

        flushed = buffer.flush(10)
        assert len(flushed) == 2
        assert buffer.get(10) == []

        buffer.add(10, {"overall": 95, "timestamp": 6.0})
        closed = buffer.close_session(10)
        assert len(closed) == 1
        assert 10 not in buffer.buffers


class TestVisionPipeline:
    def test_process_frame_uses_detector_and_landmark_extractor(self):
        from vision.pipline import VisionPipeline

        detector = Mock()
        detector.detect.return_value = {"raw": "data"}

        pipeline = VisionPipeline(detector=detector)
        pipeline.landmark_extractor = Mock()
        pipeline.landmark_extractor.filter_landmarks.return_value = {
            "pose": {"nose": {"x": 0.5, "y": 0.2}},
            "face": None,
            "hands": [],
        }

        result = pipeline.process_frame("frame-1")

        detector.detect.assert_called_once_with(
            "frame-1",
            pose_mode=True,
            face_mode=False,
            hand_mode=False,
        )
        pipeline.landmark_extractor.filter_landmarks.assert_called_once_with({"raw": "data"})
        assert result["pose"]["nose"]["x"] == 0.5

    def test_pipeline_yields_one_landmark_list_per_chunk(self, monkeypatch):
        import vision.pipline as pipeline_module

        class FakeVideoExtractor:
            def __init__(self, video_path):
                assert video_path == "demo.mp4"

            def get_chunks(self, chunk_sec, target_fps):
                assert chunk_sec > 0
                assert target_fps > 0
                yield ["a", "b"]
                yield ["c"]

        detector = Mock()
        pipeline = pipeline_module.VisionPipeline(detector=detector)
        pipeline.process_frame = Mock(
            side_effect=[
                {"pose": {"nose": {"x": 0.1, "y": 0.2}}},
                {},
                {"pose": {"nose": {"x": 0.2, "y": 0.2}}},
            ]
        )

        monkeypatch.setattr(pipeline_module, "VideoExtractor", FakeVideoExtractor)

        chunks = list(pipeline.pipline(video_path="demo.mp4"))

        assert [len(chunk) for chunk in chunks] == [1, 1]
        assert pipeline.process_frame.call_count == 3


class TestSessionAnalysisService:
    def test_process_chunk_builds_snapshot_without_running_video_pipeline(self):
        from services.session_analysis_service import SessionAnalysisService

        analytics = Mock()
        analytics.run_full_analysis.return_value = {
            "focus": 80.0,
            "posture": 90.0,
            "overall": 85.0,
        }

        session_buffer = Mock()
        session_buffer.should_flush.return_value = False
        repository = Mock()

        service = SessionAnalysisService(
            analytics=analytics,
            detector=Mock(),
            session_buffer=session_buffer,
            snapshot_repository=repository,
        )

        result = service._process_chunk(
            session_id=7,
            chunk_index=2,
            landmarks_list=[sample_frame(), sample_frame(0.01)],
            timestamp_offset=5.0,
        )

        assert result == {
            "session_id": 7,
            "chunk_index": 2,
            "timestamp": 8.0,
            "frames_count": 2,
            "scores": {"focus": 80.0, "posture": 90.0, "overall": 85.0},
        }

        analytics.run_full_analysis.assert_called_once()
        session_buffer.add.assert_called_once_with(
            session_id=7,
            snapshot={
                "focus": 80.0,
                "posture": 90.0,
                "overall": 85.0,
                "timestamp": 8.0,
            },
        )
        repository.create_snapshots.assert_not_called()

    def test_process_offline_uses_fake_pipeline_and_flushes(self, monkeypatch):
        import services.session_analysis_service as service_module

        class FakePipeline:
            last_instance = None

            def __init__(self, detector):
                self.detector = detector
                self.closed = False
                FakePipeline.last_instance = self

            def pipline(self, video_path):
                assert video_path == "video.mp4"
                yield [sample_frame()]
                yield []
                yield [sample_frame(), sample_frame(0.01)]

            def close(self):
                self.closed = True

        monkeypatch.setattr(service_module, "VisionPipeline", FakePipeline)

        analytics = Mock()
        analytics.run_full_analysis.return_value = {
            "focus": 80.0,
            "overall": 80.0,
        }

        session_buffer = Mock()
        session_buffer.should_flush.return_value = False
        session_buffer.flush.return_value = [
            {"focus": 80.0, "overall": 80.0, "timestamp": 0.0}
        ]
        repository = Mock()

        service = service_module.SessionAnalysisService(
            analytics=analytics,
            detector=Mock(),
            session_buffer=session_buffer,
            snapshot_repository=repository,
        )

        response = service.process_offline(video_path="video.mp4", session_id=12)

        assert response.session_id == 12
        assert response.status == "success"
        assert analytics.run_full_analysis.call_count == 2
        session_buffer.flush.assert_called_once_with(12)
        repository.create_snapshots.assert_called_once()
        assert FakePipeline.last_instance.closed is True


class TestOfflineService:
    @pytest.mark.asyncio
    async def test_process_success(self):
        from schemas.offline import OfflineResponse
        from services.offline_service import OfflineService

        video = types.SimpleNamespace(filename="presentation.mp4")

        storage = Mock()
        storage.save_temp = Mock()

        async def fake_save_temp(upload):
            assert upload is video
            return "/tmp/presentation.mp4"

        storage.save_temp.side_effect = fake_save_temp

        analysis_service = Mock()
        analysis_service.process_offline.return_value = OfflineResponse(
            session_id=25,
            status="success",
        )

        service = OfflineService(
            video=video,
            video_storage=storage,
            session_analysis_service=analysis_service,
        )

        response = await service.process(session_id=25)

        assert response.session_id == 25
        assert response.status == "success"
        analysis_service.process_offline.assert_called_once_with(
            video_path="/tmp/presentation.mp4",
            session_id=25,
        )
        storage.delete.assert_called_once_with("/tmp/presentation.mp4")
        assert service.video_path is None

    @pytest.mark.asyncio
    async def test_process_deletes_temp_file_even_when_analysis_fails(self):
        from core.exceptions import VisionProcessingError
        from services.offline_service import OfflineService

        video = types.SimpleNamespace(filename="broken.mp4")
        storage = Mock()

        async def fake_save_temp(upload):
            return "/tmp/broken.mp4"

        storage.save_temp.side_effect = fake_save_temp

        analysis_service = Mock()
        analysis_service.process_offline.side_effect = RuntimeError("boom")

        service = OfflineService(
            video=video,
            video_storage=storage,
            session_analysis_service=analysis_service,
        )

        with pytest.raises(VisionProcessingError):
            await service.process(session_id=3)

        storage.delete.assert_called_once_with("/tmp/broken.mp4")
        assert service.video_path is None
