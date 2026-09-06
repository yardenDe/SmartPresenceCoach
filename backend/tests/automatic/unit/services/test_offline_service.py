import types
from unittest.mock import Mock

import pytest


@pytest.mark.asyncio
async def test_process_success():
    from schemas.analysis import Analysis, VisualAnalysis
    from services.offline_service import OfflineService

    video = types.SimpleNamespace(filename="presentation.mp4")
    storage = Mock()

    async def fake_save_temp(upload):
        assert upload is video
        return "/tmp/presentation.mp4"

    storage.save_temp.side_effect = fake_save_temp
    frame_extractor = Mock()
    frame_extractor.get_chunks.return_value = [["frame-1"], ["frame-2"]]
    audio_extractor = Mock()
    audio_extractor.stream.return_value = [[0.1], [0.2]]
    analysis_service = Mock()
    analysis = Analysis(visual=VisualAnalysis(overall=80))
    analysis_service.process.side_effect = [analysis, Analysis()]
    session_service = Mock()
    service = OfflineService(
        storage=storage,
        frame_extractor=frame_extractor,
        audio_extractor=audio_extractor,
        analysis_service=analysis_service,
        session_service=session_service,
    )

    response = await service.process(video=video, user_id=7, session_id=25)

    assert response.session_id == 25
    assert response.status == "success"
    session_service.require_owned_session.assert_called_once_with(7, 25)
    frame_extractor.get_chunks.assert_called_once_with("/tmp/presentation.mp4")
    assert analysis_service.process.call_count == 2
    session_service.add_analysis.assert_called_once_with(
        session_id=25,
        timestamp=0.0,
        analysis=analysis,
    )
    session_service.end.assert_called_once_with(7, 25)
    storage.delete.assert_called_once_with("/tmp/presentation.mp4")


@pytest.mark.asyncio
async def test_process_deletes_temp_file_even_when_analysis_fails():
    from core.exceptions import VisionProcessingError
    from services.offline_service import OfflineService

    video = types.SimpleNamespace(filename="broken.mp4")
    storage = Mock()

    async def fake_save_temp(upload):
        return "/tmp/broken.mp4"

    storage.save_temp.side_effect = fake_save_temp
    frame_extractor = Mock()
    frame_extractor.get_chunks.return_value = [["frame"]]
    audio_extractor = Mock()
    audio_extractor.stream.return_value = [[0.1]]
    analysis_service = Mock()
    analysis_service.process.side_effect = RuntimeError("boom")
    session_service = Mock()
    service = OfflineService(
        storage=storage,
        frame_extractor=frame_extractor,
        audio_extractor=audio_extractor,
        analysis_service=analysis_service,
        session_service=session_service,
    )

    with pytest.raises(VisionProcessingError):
        await service.process(video=video, user_id=7, session_id=3)

    session_service.end.assert_not_called()
    storage.delete.assert_called_once_with("/tmp/broken.mp4")
