class ProviderError(Exception):
    """Raised when an external provider call (URL fetch, LLM) fails."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.message = message
        self.detail = detail
