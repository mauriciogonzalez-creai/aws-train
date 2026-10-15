# Paso 00 — Alerta de presupuesto

```bash
uv run python steps/00_budget.py
```

## Qué hace

Crea un **AWS Budget** mensual llamado `aws-train-budget` con el límite de `BUDGET_LIMIT_USD` (10 USD por defecto) y te manda un correo a `BUDGET_EMAIL` cuando:

- el gasto **real** del mes pasa el **80 %** del límite, o
- el gasto **pronosticado** para el mes pasa el **100 %**.

Es el primer paso a propósito: ningún paso crea algo facturable antes de que exista esta alerta.

## Qué no hace

Un Budget **avisa, no corta**. Si te llega el correo, AWS sigue cobrando hasta que borres los recursos: corre el [paso 99 (teardown)](step-99-teardown.md).

El correo puede tardar varias horas en llegar: AWS actualiza los datos de costo pocas veces al día.

## Conceptos

- **AWS Budgets** es un servicio global; el script siempre lo llama en `us-east-1`, aunque cambies `AWS_REGION`.
- El Budget lleva el tag `project=aws-train`, como todo lo que crea el demo.

## Si lo vuelves a correr

Si el Budget ya existe, el script lo dice y no hace nada. Para cambiar el límite, bórralo en la consola (*Billing → Budgets*) y vuelve a correr el paso.

## Errores comunes

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Configuration error: BUDGET_EMAIL is required` | Falta la variable | `export BUDGET_EMAIL=tu-correo@ejemplo.com` |
| `AWS credentials are missing or expired` | Sesión de `aws login` caducada | `aws login --profile aws-train` |
| `AccessDeniedException` | Tu usuario no puede ver Billing | Con el usuario root, activa *Account → IAM user and role access to Billing information* |

Siguiente: [paso 01 — Execution Role](step-01-execution-role.md).
