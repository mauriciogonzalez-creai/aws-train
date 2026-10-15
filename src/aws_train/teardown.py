"""Deletion plan for the Teardown (Step 99): what to delete, and in which order."""

from collections.abc import Iterable
from dataclasses import dataclass

from aws_train.naming import (
    BUDGET_NAME,
    MODEL_NAME,
    PREFIX,
    ROLE_NAME,
    SERVERLESS_ENDPOINT_NAME,
)

DELETION_ORDER = ("endpoint", "endpoint-config", "model", "bucket", "budget", "role")
GUARDRAIL_KINDS = frozenset({"budget", "role"})
_SAGEMAKER_KINDS = frozenset({"endpoint", "endpoint-config", "model"})


@dataclass(frozen=True)
class Deletion:
    kind: str
    name: str


def _from_arn(arn: str) -> Deletion | None:
    parts = arn.split(":", 5)
    if len(parts) != 6:
        return None
    service, resource = parts[2], parts[5]
    if service == "s3":
        return Deletion("bucket", resource)
    if service == "sagemaker":
        kind, _, name = resource.partition("/")
        if kind in _SAGEMAKER_KINDS:
            return Deletion(kind, name)
    return None


def plan_deletions(
    tagged_arns: Iterable[str], *, bucket: str, keep_guardrails: bool
) -> list[Deletion]:
    """Ordered deletions: endpoints before their configs, configs before models, then storage.

    Always includes the demo's known resources, so the Teardown works without the state
    file or the Tagging API. Adds any other tagged demo resource; ignores Training Jobs
    (AWS can't delete them and they cost nothing at rest) and names outside the demo prefix.
    """
    planned = {
        Deletion("endpoint", SERVERLESS_ENDPOINT_NAME),
        Deletion("endpoint-config", SERVERLESS_ENDPOINT_NAME),
        Deletion("model", MODEL_NAME),
        Deletion("bucket", bucket),
        Deletion("budget", BUDGET_NAME),
        Deletion("role", ROLE_NAME),
    }
    for arn in tagged_arns:
        deletion = _from_arn(arn)
        if deletion is not None and deletion.name.startswith(PREFIX):
            planned.add(deletion)
    if keep_guardrails:
        planned = {deletion for deletion in planned if deletion.kind not in GUARDRAIL_KINDS}
    return sorted(planned, key=lambda d: (DELETION_ORDER.index(d.kind), d.name))
