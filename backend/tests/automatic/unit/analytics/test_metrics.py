import pytest

from analytics.visual.metrics.face_direction_analyzer import FaceDirectionAnalyzer
from analytics.visual.metrics.hand_movement_analyzer import HandMovementAnalyzer
from analytics.visual.metrics.head_movement_analyzer import HeadMovementAnalyzer
from analytics.visual.metrics.movement_amount_analyzer import MovementAmountAnalyzer
from analytics.visual.metrics.movement_variation_analyzer import MovementVariationAnalyzer
from analytics.visual.metrics.shoulder_tilt_analyzer import ShoulderTiltAnalyzer
from media.config import TARGET_FPS


@pytest.mark.parametrize("analyzer, expected", [
    (FaceDirectionAnalyzer, 0.0),
    (ShoulderTiltAnalyzer, 0.0),
    (HeadMovementAnalyzer, 0.0),
    (MovementVariationAnalyzer, 0.0),
    (MovementAmountAnalyzer, 0.005 / 0.30 * TARGET_FPS),
    (HandMovementAnalyzer, 0.005 / 0.30 * TARGET_FPS),
])
def test_analyzer_measures_flat_landmarks(sample_frame, analyzer, expected):
    frames = [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
    assert analyzer().analyze(frames) == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("analyzer", [
    FaceDirectionAnalyzer, ShoulderTiltAnalyzer, HeadMovementAnalyzer,
    MovementVariationAnalyzer, MovementAmountAnalyzer, HandMovementAnalyzer,
])
def test_missing_points_do_not_produce_measurements(analyzer):
    assert analyzer().analyze([{}, {}]) is None
