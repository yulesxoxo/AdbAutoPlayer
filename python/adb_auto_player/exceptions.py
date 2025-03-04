class TimeoutException(Exception):
    """Raised when an operation exceeds the given timeout."""

    pass


class UnsupportedResolutionException(Exception):
    """Raised when the resolution is not supported."""

    pass


class AdbException(Exception):
    """Raised for any Adb related issues."""

    pass


class NotFoundException(Exception):
    pass


class NotInitializedError(Exception):
    pass


class NoPreviousScreenshotException(Exception):
    """Previous Screenshot required but does not exist."""

    pass
