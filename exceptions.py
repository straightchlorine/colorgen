"""Exception hierarchy for colorgen."""


class ColorgenException(Exception):
    """Base exception for all colorgen errors."""

    pass


class InvalidImageError(ColorgenException):
    """Raised when image path is invalid or image cannot be loaded."""

    pass


class InvalidColorError(ColorgenException):
    """Raised when color values are invalid (e.g., RGB out of range)."""

    pass


class ConfigWriteError(ColorgenException):
    """Raised when configuration file cannot be written."""

    pass


class ModelLoadError(ColorgenException):
    """Raised when ML model cannot be loaded (for future ML integration)."""

    pass


class ValidationError(ColorgenException):
    """Raised when input validation fails."""

    pass
