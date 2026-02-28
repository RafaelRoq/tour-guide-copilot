"""Custom exceptions for Tour Guide Copilot."""


class CopilotError(Exception):
    """Base exception for all copilot errors."""


class ConfigError(CopilotError):
    """Raised when configuration is missing or invalid."""


class PromptError(CopilotError):
    """Raised when a prompt file is missing or unreadable."""


class SchemaError(CopilotError):
    """Raised when the model's JSON output doesn't match the expected schema."""

    def __init__(self, message: str, raw_response: str = ""):
        super().__init__(message)
        self.raw_response = raw_response


class DocumentTooLargeError(CopilotError):
    """Raised when the input document exceeds the configured token limit."""

    def __init__(self, char_count: int, limit: int):
        self.char_count = char_count
        self.limit = limit
        super().__init__(
            f"Document is ~{char_count:,} characters ({char_count // 4:,} estimated tokens). "
            f"Limit is {limit:,} characters. "
            f"Consider trimming the document or raising MAX_DOCUMENT_CHARS in .env."
        )
