import types
from unittest.mock import Mock

import pytest


@pytest.mark.asyncio
async def test_process_success():
    from schemas.offline import OfflineResponse
    from services.offline_service import OfflineService

    video = types.SimpleNamespace(filename="presentation.mp4")
    storage = Mock()

    async def fake_save_temp(upload):
        assert upload is video
        return "/tmp/presentation.mp4"

    storage.save_temp.side_effect = fake_save_temp
    analysis_service = Mock()
    analysis_service.process_offline.return_value = OfflineResponse(
        session_id=25, status="success"
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
        video_path="/tmp/presentation.mp4", session_id=25
    )
    storage.delete.assert_called_once_with("/tmp/presentation.mp4")
    assert service.video_path is None


@pytest.mark.asyncio
async def test_process_deletes_temp_file_even_when_analysis_fails():
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
