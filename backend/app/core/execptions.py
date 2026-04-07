from fastapi import status
from fastapi.responses import JSONResponse

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



async def app_exceptions_handler(exc: AppError):
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