# ADR-002: `aws login` with an IAM User for the Learner, a Dedicated Execution Role for SageMaker

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** auth, security, aws

## Context

Each Learner runs the demo against their own personal AWS account. Long-lived access keys in `~/.aws/credentials` are the most common way a personal account gets compromised, and the guide would be teaching that habit. SageMaker itself also needs permissions (S3, image pull) that are separate from the person running the scripts.

The first version of this ADR chose IAM Identity Center SSO. On a personal account, giving Identity Center users access to the AWS account requires enabling AWS Organizations, and the tech lead's first run was blocked there: the setup rejected every email offered for the management account (2026-10-15).

## Decision

We will have the Learner create an IAM user with console access and the `AdministratorAccess` and `SignInLocalDevelopmentAccess` managed policies, and authenticate the CLI and SDKs with `aws login --profile aws-train` (AWS CLI ≥ 2.32.0), which issues temporary credentials from a browser sign-in. A Step creates a dedicated SageMaker Execution Role scoped to the demo's S3 bucket. The scripts read the profile name from configuration and never handle keys.

## Consequences

### Positive

- No long-lived credentials on the Learner's disk; credentials refresh automatically for up to 12 hours.
- No AWS Organizations or Identity Center setup: one IAM user and one command.
- The Execution Role makes the person-vs-service distinction explicit, which is a core SageMaker concept.

### Negative

- boto3 needs the `crt` extra (`boto3[crt]`) to read `aws login` profiles; without it every Step fails with `MissingDependencyException` (verified 2026-10-15 with botocore from boto3 1.43).
- Requires a recent AWS CLI (≥ 2.32.0); Learners with an older CLI must upgrade first.
- An IAM user with `AdministratorAccess` is broad; acceptable only because the account is a personal lab account. The guide must require MFA on it.

### Neutral

- The Teardown does not delete the IAM user; the Learner keeps it for future use.

## Alternatives considered

- **IAM Identity Center + SSO:** AWS's recommended pattern for organizations, and the first choice of this ADR. Rejected for personal accounts: it requires AWS Organizations, whose setup blocked the first real run.
- **IAM user + access keys:** simpler, but leaves permanent keys on disk; a leak exposes the Learner's own billing. Rejected.
- **AWS CloudShell:** no local credentials, but the session is ephemeral and uv/Python must be reinstalled each time. Rejected as primary.
- **Root user with `aws login`:** works with no extra policy, but normalizes using root for daily work. Rejected.

## References

- GRZR-11 — Training de AWS
- https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html
- https://aws.amazon.com/blogs/security/simplified-developer-access-to-aws-with-aws-login
