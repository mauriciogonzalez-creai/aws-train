# 📜 Resumen — Políticas de Contribución de Código

> **⚠️ Template file.** This is the canonical copy of the generic contribution policies, mirrored from the organization's documentation source. To use it in a project, copy this file to `docs/POLICIES.md` and treat it as read-only (sync changes from the source, never edit locally). Organization-specific rules (named people or teams, domains, source links) live in the override file named by `policy_overrides` in `org/org.json` (default `org/POLICIES.md`); read it together with this document.
>
> **🇪🇸 Language exception:** This document is in Spanish by deliberate choice. It is human-facing internal documentation for your organization's developers (not code, not agent-facing artifact). The "Everything in English" rule in CLAUDE.md applies to code, configs, commits, identifiers, agent-facing files (CONTEXT.md, ADRs, CLAUDE.md) — NOT to internal human policy docs sourced from the organization's documentation.

> **Fuente:** ver `org/POLICIES.md` (enlace a la fuente de la organización).
> **Owner del paquete:** Tech Leads & Engineering Managers
> **Última actualización del original:** 2025-12-18
> **Canal de feedback:** `#developers` / `#engineering-practices` en Slack

El paquete está diseñado para soportar **100+ desarrolladores con alta rotación entre proyectos**, garantizando calidad, consistencia y velocidad.

---

## 1. 🌍 Idioma y Nomenclatura

### Idioma
- **TODO en inglés**: código, variables, funciones, comentarios, docstrings, commits, PRs, nombres de archivos.
- **Español permitido SOLO** en documentación de usuario final y mensajes de UI del producto cuando el mercado es hispanohablante. Nunca en comentarios, docstrings, mensajes de CLI/log ni tests, aunque la conversación con el agente sea en español.

### Repositorios
- Formato: `{cliente}-{proyecto}-{identificador}` → `acme-ecommerce-backend`, `globex-erp-api`.
- Reglas: kebab-case con guiones (no underscores), breve, sin caracteres especiales, sin números, sin abreviaturas, sin versiones.
- Organización GitHub: **Teams nivel 1 = Cliente**, **Sub-teams nivel 2 = Proyecto**.

### Branches
- Formato: `[type]/[ticket]-[description]` → `feature/PROJ-123-user-authentication`.
- Tipos válidos: `feature`, `fix`, `hotfix`, `bugfix`, `docs`, `test`, `perf`, `build`, `ci`, `chore`, `refactor`.

### Commits (Conventional Commits, obligatorio)
- Formato: `<type>(<scope>): <subject> [TICKET]`.
- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Subject en mayúscula, sin punto final, descriptivo (no "fix", "update").
- **Cadencia (agente IA):** el agente NUNCA commitea autónomamente durante la implementación de un plan. Los commits son responsabilidad del dev, agrupados por **hito vertical** (feature/test/docs como commits lógicos separados, NO uno por checkbox de `tasks.md` ni uno por batch). Al cerrar el plan, el agente debe proponer una agrupación de commits; el dev acepta, ajusta o commitea manualmente. Razón: una implementación promedio genera 15-20 cambios; un commit por cambio convierte la historia en ruido inútil.
- **Atomicidad:** "atomic commit" significa "agrupado por propósito lógico y compilable independientemente", NO "el commit más pequeño posible".

### Naming por lenguaje
- **Python (PEP 8)**: `snake_case` para variables/funciones, `PascalCase` clases, `UPPER_SNAKE_CASE` constantes, prefijo `_` para privadas.
- **JS/TS**: `camelCase` variables, `PascalCase` clases/componentes/interfaces, `UPPER_SNAKE_CASE` constantes. Archivos React en `PascalCase.tsx`, hooks con prefijo `use`.
- **Go**: `PascalCase` exportadas, `camelCase` privadas, archivos en `snake_case.go`.
- **Java**: `camelCase` métodos, `PascalCase` clases, packages en `lowercase.dot.notation`.

---

## 2. 🌳 Estrategia de Branching (Gitflow → Trunk-Based, 4 stages)

Evolución progresiva con **gatekeeps** medibles entre etapas:

| Stage | Foco | Lead Time | Deploy freq | Change failure rate |
|---|---|---|---|---|
| **1. Strengthen Gitflow** | CI básico, code reviews, branches < 5 días | < 10 días | Semanal | < 15% |
| **2. Automate & Shorten** | Test automation, feature flags, develop→master sync | < 5 días | Cada 2-3 días | < 10% |
| **3. Trunk Pilot** | Pilot trunk + canary + rollback automático | < 2 días | Diario | < 5% |
| **4. Full Trunk** | Trunk-based total, deploys múltiples por día | < 1 día | Múltiple/día | < 5% |

**Feature flags obligatorios desde Stage 2** (LaunchDarkly, Unleash, PostHog). Pitfalls a evitar: saltar stages, feature branches largas, tests insuficientes, monitoring débil.

---

## 3. 🔀 Workflow de Contribución (Feature Branch)

1. **Setup**: configurar `user.name` / `user.email` con el dominio corporativo de la organización (ver `org/POLICIES.md`), generar SSH key (ed25519), instalar pre-commit.
2. **Crear branch** desde `develop` actualizado: `git checkout -b feature/PROJ-123-description`.
3. **Desarrollar** con commits atómicos (cada commit compila y pasa tests).
4. **Sincronizar diariamente** con `git fetch && git rebase origin/develop` (preferir rebase sobre merge).
5. **Push** con `--force-with-lease` (nunca `--force` solo).
6. **PR**: usar template, asignar reviewers, vincular ticket Jira, esperar CI/CD.
7. **Code review**: cambios en commits separados, squash al final.
8. **Cleanup**: eliminar branch local y remota, `git fetch --prune`.

### Hotfix Workflow
- Partir de `main`, crear `hotfix/critical-...`, PR directo a `main`, después **resincronizar a `develop`** para evitar regresión.

### Pull Request — Requisitos obligatorios
- ✅ Template completo con checklist (`.github/pull_request_template.md`).
- ✅ Mínimo **1 aprobación** antes de merge.
- ✅ CI/CD checks passed (lint, test, security).
- ✅ **Squash commits** antes de merge (1 commit final).
- ✅ Branch up-to-date con `develop`/`main`.
- ✅ Validar que no se eliminen archivos críticos (routes, Providers, Kernel.php, router.js, package.json, composer.json).

### Anuncio del PR
Dónde se piden reviews de cada repo. `/axis-create-pr` lo usa para ofrecer el anuncio del PR (siempre mostrado y confirmado antes de enviarse). La clave es **el repo donde se abre el PR**, no el ticket: un ticket de un equipo puede abrir PRs en el repo de otro. Las filas `Jira: <KEY>` son respaldo para repos sin fila propia. Sin coincidencia, pregunta y ofrece agregar la fila.

| Repo | Equipo | Canal de aprobaciones |
|---|---|---|
| `<org>/<repo>` | <equipo> | `#<canal>` |
| `Jira: <KEY>` | <equipo> | `#<canal>` |

---

## 4. ✅ Code Quality Standards

### Coverage obligatorio

| Proyecto | Mínimo | Target | Bloquea merge si < |
|---|---|---|---|
| Backend/API | 70% | 80%+ | 60% |
| Frontend | 60% | 70%+ | 50% |
| Libraries | 80% | 90%+ | 70% |
| **Critical paths** (pagos, auth, encryption, PII) | 100% | 100% | 100% |

### SonarQube Quality Gates (bloqueantes)
- Bugs: **0** · Vulnerabilities: **0** · Coverage ≥ 70% · Maintainability/Reliability/Security Rating: **A** · Duplicated lines < 3%.

### Tipos de tests
- **Pirámide**: 80% unit, 15% integration, 5% E2E.
- **Unit obligatorio** (pytest, Jest, `go test`).
- **Integration obligatorio** para APIs (TestClient FastAPI, etc.). Para tests aislados se recomienda **SQLite con dependency override**.
- **E2E recomendado** para flujos críticos UI (Playwright, Cypress).

### Complejidad
- Cyclomatic complexity: función ≤ 10 (warn) / ≤ 15 (error). Funciones < 50 líneas (ideal < 30), clases < 300, módulos < 500.

### Code Style
- **Python**: `black` (line-length 100), `isort` (profile black), `pylint`, `mypy` con `disallow_untyped_defs`.
- **JS/TS**: ESLint + Prettier (`printWidth: 100`, `singleQuote: true`).
- **Go**: `go fmt`, `go vet`, `golangci-lint`.

### Documentación
- **Docstrings/JSDoc obligatorios** para funciones públicas, APIs, código de seguridad y algoritmos complejos. El docstring explica el propósito, el contrato y los casos no obvios: es el único lugar para esa explicación.
- **Sin comentarios por defecto.** El código se lee solo: nombres precisos, funciones pequeñas, constantes con nombre. Un comentario existe únicamente si es **obligatorio** (cabecera de licencia, directiva de herramienta: `noqa`, `type: ignore`, `shellcheck disable`, `eslint-disable`, `neutrality:allow`; o `TODO(username): desc [PROJ-123]` con ticket) o por una **necesidad puntual** que el código no puede expresar (workaround de un bug externo con su enlace, un invariante de seguridad) — una línea, no un párrafo.
- Nunca: narrar lo que hace el código, contar la historia del cambio ("antes hacía X", "se arregló el 2026-…"), justificar decisiones de diseño o dejar código comentado. Eso va al commit, al PR o a un ADR.

### Anti-patterns a evitar
- God Objects, nested conditionals (usar guard clauses), magic numbers, código duplicado, funciones que hacen demasiado (violan SRP).

---

## 5. 🪝 Git Hooks y Pre-commit (obligatorio en todos los repos)

- **Framework**: `pre-commit` instalado en cada repo + `commit-msg` hook.
- **Hooks generales**: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files` (máx 1MB), `check-merge-conflict`, `detect-private-key`, `detect-aws-credentials`.
- **Secrets**: `detect-secrets` con `.secrets.baseline` versionado.
- **Python**: `black`, `isort`, `flake8`, `mypy`. **JS/TS**: `eslint`, `prettier`. **Otros**: Terraform (`terraform_fmt/validate/docs/tflint`), Docker (`hadolint`), SQL (`sqlfluff`), Go.
- **Ruff** recomendado para Python (10–1000x más rápido, unifica flake8/isort/pyupgrade).
- **Commit message validation**: commitizen valida Conventional Commits.
- `--no-verify` **solo para emergencias** (hotfixes críticos).

---

## 6. 🔐 Seguridad y Secrets Management

### Prohibiciones absolutas
- ❌ **NUNCA** commits de secrets, passwords, API keys, tokens, connection strings.
- ❌ **NUNCA** hardcodear URLs con credenciales.
- ❌ **NUNCA** commits de `.env`, `.env.local`, `credentials.json`, `*.pem`, `*.key`.
- ❌ **NUNCA** push directo a `main` o `develop` (branch protection enforcement).
- ❌ **NUNCA** compartir secrets por Slack/email (usar 1Password, Vault, AWS Secrets Manager).

### Método correcto
- Variables de entorno con `.env` local (en `.gitignore`) + `.env.example` commiteado.
- **Producción**: AWS Secrets Manager / Azure Key Vault / GCP Secret Manager.
- **CI/CD**: GitHub Secrets configurados por environment.

### Rotación
- API keys: cada 90 días. DB credentials: 90 días. SSH keys: 180 días. JWT signing keys: 30 días con overlap. Algoritmo recomendado: RS256 o EdDSA (no HS256 en prod).

### Procedimiento de emergencia si committeas un secret
1. **Invalidar/rotar el secret INMEDIATAMENTE** (antes que cualquier limpieza).
2. Si no se ha pusheado → `git commit --amend` o `git rebase -i`.
3. Si ya se pusheó → **BFG Repo-Cleaner** o `git filter-branch`, luego `git push --force`.
4. Notificar a `#engineering-security`, todos re-clonan el repo.
5. Documentar incidente en JIRA.

### Tools de escaneo
TruffleHog, gitleaks, detect-secrets, GitHub Secret Scanning, Snyk, Semgrep.

---

## 7. 🛠️ DevOps & CI/CD

### Infrastructure as Code (Terraform)
- Versiones explícitas de providers + `.terraform.lock.hcl` en git.
- Backend remoto configurado por cliente via archivos `.hcl`.
- Naming convention: `[project]-[resource]-[environment]` con Terraform workspaces (`dev`, `staging`, `prod`).
- Migraciones DB **siempre reversibles** y testeadas en staging.

### GitHub Actions
- **Workflows separados**: lint+test (en feature branches), deploy infra (paths: `IaC/**`), deploy service.
- Cache de dependencias (pip, npm).
- Secrets por **environment** (GitHub Environments con approval gates para prod).
- Quality gates bloqueantes: pre-commit, tests con coverage `--fail-under=70`, mypy, linting, security scan (bandit, safety, npm audit, TruffleHog, Semgrep), SonarQube Quality Gate.

### Estrategias de deployment

| Estrategia | Downtime | Uso |
|---|---|---|
| **Blue/Green** | Cero | Frontend, switch instantáneo, rollback inmediato |
| **Canary** (5%→25%→50%→100%) | Cero | Backend high-traffic, con Istio/Flagger/Argo Rollouts |
| **Rolling** | Cero | Estándar Kubernetes |
| **Feature flags** | Cero | Gradual rollout, A/B, kill switches |
| **Shadow + A/B** | Cero | ML Models |

- **Rollback automático** si error rate > 1% o latencia p99 > 500ms.
- Migraciones DB: patrón **expand-contract** (add column → backfill → write both → switch read → drop old) y nunca dropear/renombrar columnas en una sola release.

### Monitoring obligatorio
- Endpoints `/health` y `/metrics` (Prometheus format).
- Logs estructurados JSON (structlog). **Nunca** loggear passwords, tarjetas, PII, tokens.
- APM (Datadog / New Relic / Elastic APM).
- **DORA Metrics**: deployment frequency, lead time, change failure rate, time to restore.

---

## 8. 🎓 Onboarding (objetivo: 30 min)

Checklist obligatorio:
1. Git configurado (`user.name`, `user.email` con el dominio corporativo, `pull.rebase=true`, `init.defaultBranch=main`).
2. SSH key ed25519 generada y agregada a GitHub.
3. Clone del primer repo.
4. `pre-commit install` + `pre-commit install --hook-type commit-msg`.
5. IDE configurado (VSCode recomendado con GitLens, ESLint, Prettier, Black, Python, Pylance).
6. Primer PR de onboarding (`feature/ONBOARD-Name-first-pr`).

---

## 9. 📊 KPIs y Métricas que se trackean

- **DORA**: Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore Service.
- **Code Quality**: Test Coverage, Code Review Time, Technical Debt (SonarQube), Security Vulnerabilities.
- **Developer Experience**: Onboarding Time (target < 1 día en Stage 4), Build Success Rate, PR Merge Time.

---

## 10. 🆘 Recovery / Troubleshooting

- **Reflog** guarda 90 días — recupera branches/commits perdidos.
- **BFG Repo-Cleaner** para limpiar secrets de la historia.
- **`git bisect`** para encontrar commit que introdujo un bug.
- **`git stash`** para context switching seguro.
- Si todo falla → backup + re-clone fresco; reporte a `#engineering-help`.

---

## 🚦 Proceso para Proponer Cambios a Políticas

1. Crear ticket JIRA en proyecto **TECH-POLICIES**.
2. Discutir en `#developers`.
3. Review con Tech Leads.
4. Actualizar documentación en Confluence.

---

## 📚 Referencias a las páginas originales

Los enlaces a las páginas fuente de la organización viven en `org/POLICIES.md` (ver `policy_overrides` en `org/org.json`).
