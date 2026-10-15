# CLAUDE.md — aws-train

> This file is the agent's project briefing. Keep it short, accurate, and current.
> Detailed policies live in `docs/POLICIES.md`. Domain vocabulary lives in `docs/CONTEXT.md`. Architecture decisions live in `docs/adr/`.

## Stack

Python 3.12 + uv + SageMaker Python SDK / boto3 + Built-in XGBoost on Amazon SageMaker AI (Serverless Endpoint only), AWS `us-east-1`, `aws login` with an IAM user (needs `boto3[crt]`). pytest for local logic. Learner-facing guide in Spanish; everything else in English.

## Branch model

- Default and only long-lived branch: `main` — no `develop` (ADR-005, deviation from POLICIES.md)
- Branch naming: `feature/<TICKET>-<slug>` → PR into `main` — see @docs/POLICIES.md

## Pipeline (intended order)

`/axis-refine-task` → `/axis-design-feature` → `/axis-estimate` → `/axis-implement` →
`/axis-audit-pr` → `/axis-fix` (if needed) → `/axis-create-pr`. Run
`/axis-pipeline-status` any time to see which stages this branch has evidence for —
`/axis-create-pr` checks it too and pauses if `design`/`implement`/`audit` are missing.
No GitHub check enforces this; it is a convention, not a lock.

## Improving the marketplace

When you do a repeatable, generic process step no `/axis-*` skill covers, ask the dev at a
natural pause whether to propose it (`/axis-propose-improvement`): once per step, a "no" is
final, nothing is created without approval. Repo-specific steps go in this file instead.

## Critical the organization's conventions (extract — full details in @docs/POLICIES.md)

**Language:** Everything in English (code, variables, functions, comments, docstrings, CLI/log messages, test names, commits, PRs, file names). The language of the conversation never changes this: if the developer writes to you in Spanish, answer in Spanish but keep writing the code, its comments and its messages in English. Spanish ONLY in end-user docs / UI when target market is Spanish-speaking.

**Comments:** none by default. Code must read on its own — precise names, small functions, named constants — and docstrings carry the explanation (purpose, contract, non-obvious cases). A comment exists only when it is **mandatory** (license header, tool directive such as `noqa` / `type: ignore` / `shellcheck disable` / `eslint-disable`, or `TODO(user): desc [PROJ-123]`) or a **pinpoint necessity** the code cannot express (an external-bug workaround with its link, a security invariant) — one line, never a paragraph. Never narrate what the code does, tell the history of a change, justify a design decision, or leave commented-out code: that belongs in the commit, the PR or an ADR.

**Naming by language:**
- Python (PEP 8): `snake_case` vars/funcs, `PascalCase` classes, `UPPER_SNAKE_CASE` constants
- JS/TS: `camelCase` vars, `PascalCase` classes/components/interfaces, React files `PascalCase.tsx`, hooks prefixed `use`
- Go: `PascalCase` exported, `camelCase` private, files `snake_case.go`

**Conventional Commits (mandatory):** `<type>(<scope>): <subject> [TICKET]`. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.

**Commit cadence:** the agent does NOT commit autonomously during implementation. Commits are the dev's responsibility, grouped by vertical milestone (feature / test / docs as separate logical commits, not one-per-task). At the end of a plan, the agent must propose a commit grouping; the dev accepts, adjusts, or commits manually.

**Absolute prohibitions:**
- Secrets, passwords, API keys, tokens in code
- Committing `.env`, `credentials.json`, `*.pem`, `*.key`
- Direct push to `main` or `develop`
- `git push --force` (use `--force-with-lease`)

**Coverage targets:** Backend ≥70% · Frontend ≥60% · Libraries ≥80% · Critical paths (payments, auth, encryption, PII) = 100%

**Style tools:** Python (black line-100, isort, ruff, mypy) · JS/TS (ESLint + Prettier line-100 singleQuote) · Go (go fmt, golangci-lint)

## Key commands

- `uv sync` — install deps from the lockfile
- `uv run pytest` — run local-logic tests
- `uv run ruff check . && uv run black --check . && uv run mypy .` — lint
- `aws login --profile <profile>` — refresh credentials before running Steps
- `uv run python steps/<NN>_<name>.py` — run one Step (in order; the last one is the Teardown)
(Commands are the intended layout; none exist until the first change lands.)

## Architecture decisions

See `docs/adr/` for all recorded decisions. Highlights:
- ADR-001-tech-stack — Python 3.12 + uv + SageMaker SDK + Built-in XGBoost
- ADR-002-auth-strategy — `aws login` with an IAM user + dedicated Execution Role
- ADR-003-deployment-target — Serverless Endpoint only in us-east-1, cost guardrails
- ADR-004-independent-from-origo — no Origo dependencies; own ADR sequence
- ADR-005-trunk-based-branching — `main` only

## Domain context

See `docs/CONTEXT.md` for domain vocabulary and business rules specific to this project.

## Active work

See `openspec/changes/` for in-flight specifications.
