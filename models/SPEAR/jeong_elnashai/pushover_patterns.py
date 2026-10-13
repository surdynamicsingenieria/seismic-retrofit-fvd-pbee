"""Source-locked lateral load patterns for Jeong-Elnashai SPEAR pushover.

The validation workflow must not select a pushover mode from modal effective
mass. MAE 04-03 reports four unidirectional pushover cases: xp100, xn100,
yp100 and yn100. Until their exact load vectors or textual definition are
available, this module intentionally refuses to provide substitute patterns.
"""

REQUIRED_PATTERNS = ("xp100", "xn100", "yp100", "yn100")


class MissingPublishedPatternError(RuntimeError):
    """Raised when a requested pushover pattern is not source-locked."""


def get_pattern(name):
    if name not in REQUIRED_PATTERNS:
        raise ValueError(f"Unknown Jeong-Elnashai pushover pattern: {name}")
    raise MissingPublishedPatternError(
        "Published lateral load vector for "
        f"{name} is not source-locked. Do not replace it with modal effective "
        "mass selection or any calibrated surrogate."
    )
