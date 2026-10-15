"""Instance-type allowlist: Steps refuse anything outside it before calling AWS."""

TRAINING_INSTANCE_TYPE = "ml.m5.xlarge"
ALLOWED_INSTANCE_TYPES: frozenset[str] = frozenset({TRAINING_INSTANCE_TYPE})


class InstanceNotAllowedError(ValueError):
    """Raised for an instance type outside ALLOWED_INSTANCE_TYPES."""


def require_allowed(instance_type: str) -> str:
    """Return ``instance_type`` if allowlisted, otherwise raise InstanceNotAllowedError."""
    if instance_type not in ALLOWED_INSTANCE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_INSTANCE_TYPES))
        raise InstanceNotAllowedError(
            f"Instance type {instance_type!r} is not allowed; use one of: {allowed}"
        )
    return instance_type
