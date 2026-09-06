from fastapi import status, Request
from fastapi.responses import JSONResponse

from core.logger import get_logger

logger = get_logger("app.core.exceptions")


class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "INTERNAL_SERVER_ERROR"
    message = "An unexpected error occurred"

    def __init__(self, message: str | None = None, details: dict | None = None):
        if message:
            self.message = message
        self.details = details or {}

class AuthError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTH_ERROR"
    message = "Authentication failed"
    
class InvalidUserNameError(AuthError):
    code = "INVALID_CREDENTIALS"
    message = "Invalid user name, try another one"

class InvalidCredentialsError(AuthError):
    code = "INVALID_CREDENTIALS"
    message = "Incorrect user name or password"

class TokenExpiredError(AuthError):
    code = "TOKEN_EXPIRED"
    message = "Session has expired, please log in again"

class InvalidTokenError(AuthError):
    code = "INVALID_TOKEN"
    message = "The provided token is invalid or corrupted"

class UnauthorizedError(AuthError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "UNAUTHORIZED_ACCESS"
    message = "You do not have permission to perform this action"

class ResourceNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "RESOURCE_NOT_FOUND"
    message = "The requested resource was not found"

class UserNotFoundError(ResourceNotFoundError):
    code = "USER_NOT_FOUND"
    message = "The requested user does not exist in our system"

class SessionNotFoundError(ResourceNotFoundError):
    code = "SESSION_NOT_FOUND"
    message = "Session not found"

class ReportNotFoundError(ResourceNotFoundError):
    code = "REPORT_NOT_FOUND"
    message = "Report not found"

class SnapshotsNotFoundError(ResourceNotFoundError):
    code = "SNAPSHOTS_NOT_FOUND"
    message = "No snapshots found for this session"

class ValidationError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "VALIDATION_ERROR"
    message = "The request data is invalid"

class InvalidFrameError(ValidationError):
    code = "INVALID_FRAME_DATA"
    message = "The provided frame data is invalid for analysis"

class MissingFieldsError(ValidationError):
    code = "MISSING_FIELDS"
    message = "Mandatory fields are missing from the request"


class VideoProcessingError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "VIDEO_PROCESSING_ERROR"
    message = "Video could not be processed"


class VideoSaveError(VideoProcessingError):
    code = "VIDEO_SAVE_ERROR"
    message = "Video could not be saved"


class InvalidVideoError(VideoProcessingError):
    code = "INVALID_VIDEO"
    message = "Video is empty or not readable"


class VisionProcessingError(VideoProcessingError):
    code = "VISION_PROCESSING_ERROR"
    message = "Video analysis failed"


class AudioExtractionError(VideoProcessingError):
    code = "AUDIO_EXTRACTION_ERROR"
    message = "Audio could not be extracted"


class NoLandmarksError(VideoProcessingError):
    code = "NO_LANDMARKS"
    message = "No body landmarks were detected"


class AnalyticsProcessingError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "ANALYTICS_PROCESSING_ERROR"
    message = "Analysis failed"

class LLMUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "LLM_UNAVAILABLE"
    message = "LLM is currently unavaliable."

class EmailUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "EMAIL_UNAVAILABLE"
    message = "Email delivery is currently unavailable"

class PdfUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "PDF_UNAVAILABLE"
    message = "PDF generation is currently unavailable"


class DatabaseError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "DATABASE_ERROR"
    message = "Database operation failed"


async def app_exceptions_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "event=app.error code=%s status=%s path=%s",
        exc.code,
        exc.status_code,
        request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def unhandled_exceptions_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("event=app.unhandled_error path=%s", request.url.path)

    error = AppError()
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            }
        },
    )
