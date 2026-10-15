# ADR-004: Independent from the Origo Platform

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** boundary, scope

## Context

GRZR-11's description says the training is "aligned with ADR-001 and ADR-005" and with Origo. Those ADRs belong to the Origo platform, not to this repo. Inheriting them would couple a standalone training to another product's decisions and make this repo's ADR numbers ambiguous.

## Decision

We will keep this repo independent of Origo: it has its own ADR sequence starting at ADR-001, depends on no Origo code, data, accounts or infrastructure, and justifies every choice on its own terms.

## Consequences

### Positive

- The training stays valid if Origo's stack changes.
- No ambiguity when someone cites "ADR-001" inside this repo.

### Negative

- If a Learner later works on Origo, the guide does not bridge to Origo's patterns; that bridge is out of scope.

### Neutral

- GRZR-11's description should drop its Origo/ADR-001/ADR-005 references to avoid misleading readers.

## Alternatives considered

- **Align with Origo's ADR-001/ADR-005:** rejected by the tech lead — the project must stand alone.

## References

- GRZR-11 — Training de AWS
