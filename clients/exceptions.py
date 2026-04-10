class QuotaExhaustedError(RuntimeError):
    """Non-retryable: hard quota exhausted."""
    pass