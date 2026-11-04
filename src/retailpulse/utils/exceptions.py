class RetailPulseError(Exception):
    """Base exception for expected pipeline errors."""


class ConfigurationError(RetailPulseError):
    """Raised when required runtime configuration is missing."""


class PipelineError(RetailPulseError):
    """Raised when a pipeline stage cannot complete safely."""


class ExtractionError(PipelineError):
    """Raised when extraction from source database fails."""


class IngestionError(PipelineError):
    """Raised when loading or staging into storage/warehouse fails."""


class ValidationError(RetailPulseError):
    """Raised when data quality contracts or schema assertions fail."""
