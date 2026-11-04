class RetailPulseError(Exception):
    """Base exception for expected pipeline errors."""


class ConfigurationError(RetailPulseError):
    """Raised when required runtime configuration is missing."""


class PipelineError(RetailPulseError):
    """Raised when a pipeline stage cannot complete safely."""
