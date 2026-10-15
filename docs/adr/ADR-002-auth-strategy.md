# ADR-002: IAM Identity Center SSO for the Learner, a Dedicated Execution Role for SageMaker

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** auth, security, aws

## Context

Each Learner runs the demo against their own personal AWS account. Long-lived access keys in `~/.aws/credentials` are the most common way a personal account gets compromised, and the guide would be teaching that habit. SageMaker itself also needs permissions (S3, image pull) that are separate from the person running the scripts.

## Decision

We will have the Learner authenticate with IAM Identity Center (`aws configure sso`, temporary credentials, a named profile), and a Step will create a dedicated SageMaker Execution Role scoped to the demo's S3 bucket. The scripts read the profile name from configuration and never handle keys.

## Consequences

### Positive

- No long-lived credentials on the Learner's disk.
- Teaches AWS's currently recommended access pattern from day 1.
- The Execution Role makes the person-vs-service distinction explicit, which is a core SageMaker concept.

### Negative

- Enabling IAM Identity Center on a personal account is one extra setup section before any ML happens.
- SSO sessions expire; the guide must show `aws sso login` when a Step fails with expired credentials.

### Neutral

- The Teardown does not delete the Identity Center setup; the Learner keeps it for future use.

## Alternatives considered

- **IAM user + access keys:** simpler, but leaves permanent keys on disk; a leak exposes the Learner's own billing. Rejected.
- **AWS CloudShell:** no local credentials, but the session is ephemeral and uv/Python must be reinstalled each time. Rejected as primary; may be mentioned as a fallback.

## References

- GRZR-11 — Training de AWS
