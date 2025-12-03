"""Custom exceptions helping consumers diagnose issues quickly."""
from __future__ import annotations


class KandidateError(RuntimeError):
    """Represents an expected error raised by the Kandidate runtime."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:  # pragma: no cover - inherited behavior
        return self.message
