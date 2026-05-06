"""Shared validation helpers."""


def clamp_int(value: int, minimum: int, maximum: int) -> int:
    """Clamp integer to inclusive range."""
    return max(minimum, min(maximum, value))
