class TimeoutException(Exception):
    """Raised when an operation exceeds the given timeout."""

    pass


class NotFoundException(Exception):
    """Raised when a required resource is not found."""

    pass


class UnsupportedResolutionException(Exception):
    """Raised when the resolution is not supported."""

    pass


class AdbException(Exception):
    """Raised for any Adb related issues."""

    pass
