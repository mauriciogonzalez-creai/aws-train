# ADR-005: Trunk-based Branching on main (Deviation from POLICIES.md)

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** git, process

## Context

`docs/POLICIES.md` prescribes branching from `develop` and syncing `develop`→`main`. This repo is a small training guide with one primary maintainer and no deployed environments, so an integration branch adds a merge step without protecting anything.

## Decision

We will use `main` as the only long-lived branch: `feature/<TICKET>-<slug>` branches open PRs directly into `main`. There is no `develop` branch. Direct pushes to `main` remain forbidden.

## Consequences

### Positive

- One merge per change instead of two.
- No `develop`/`main` drift to keep in sync.

### Negative

- Deviates from the organization's default; anyone reading POLICIES.md alone will expect `develop`. CLAUDE.md states the deviation.

### Neutral

- If the repo grows into a multi-maintainer product, revisit with a superseding ADR.

## Alternatives considered

- **main + develop (POLICIES default):** rejected as ceremony without benefit for this repo's size.

## References

- docs/POLICIES.md § branching
