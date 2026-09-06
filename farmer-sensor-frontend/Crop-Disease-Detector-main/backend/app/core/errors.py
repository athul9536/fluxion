class VaniError(Exception):
    """Base error carrying a farmer-friendly message and an HTTP status code."""

    status_code = 400
    message = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None, status_code: int | None = None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code


class InvalidImageError(VaniError):
    status_code = 400
    message = (
        "We couldn't read this file as an image. "
        "Please upload a clear JPG, JPEG or PNG photo of the affected plant."
    )


class ImageTooLargeError(VaniError):
    status_code = 413
    message = "That photo is too large. Please upload an image under 8 MB."


class DetectionFailedError(VaniError):
    status_code = 502
    message = "Vani couldn't analyze the image right now. Please try again."


class UnclearImageError(VaniError):
    status_code = 422
    message = (
        "I can't confidently identify a disease from this image. "
        "Please upload a clear close-up of the affected leaf."
    )


class VisionUnavailableError(VaniError):
    status_code = 503
    message = (
        "Image analysis is not configured on this server yet. "
        "Please try again later."
    )


class EmptyMessageError(VaniError):
    status_code = 400
    message = "Please type a question before sending."


class AssistantUnavailableError(VaniError):
    status_code = 503
    message = (
        "Vani AI is unavailable right now. Please try your question again in a moment."
    )


class WeatherUnavailableError(VaniError):
    status_code = 503
    message = "Weather information is unavailable right now."
