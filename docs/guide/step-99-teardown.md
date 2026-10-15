# Paso 99 — Borrar todo (teardown)

```bash
uv run python steps/99_teardown.py
```

**Corre este paso siempre al terminar.** Es lo que garantiza que tu cuenta no siga cobrando.

## Qué borra, en este orden

| # | Recurso | Por qué en este orden |
|---|---|---|
| 1 | Endpoint `aws-train-serverless` | Es lo único que podría seguir generando cobros |
| 2 | Endpoint Configuration `aws-train-serverless` | Ya nadie la usa |
| 3 | SageMaker Model `aws-train-xgb-model` | Ya nadie lo usa |
| 4 | Bucket `aws-train-<cuenta>-us-east-1` | Primero lo vacía (S3 no deja borrar un bucket con archivos) |
| 5 | Budget `aws-train-budget` | La alerta ya no hace falta |
| 6 | Execution Role `aws-train-sagemaker-execution` | Ya nadie lo asume |

Además borra el archivo local `.aws-train-state.json`.

Si algo ya no existe, lo salta y sigue. Puedes correr el teardown las veces que quieras.

## Cómo encuentra lo que borra

Combina dos fuentes:

1. **Los nombres fijos** del demo (la tabla de arriba). Funciona aunque hayas borrado `.aws-train-state.json`.
2. **El tag `project=aws-train`**: le pregunta a AWS (*Resource Groups Tagging API*) qué recursos lo llevan. Así encuentra también endpoints o modelos con otro nombre que haya creado el demo.

Solo borra recursos cuyo nombre empiece con `aws-train`. Nunca toca nada más de tu cuenta.

## Lo que no se borra

- **Training Jobs:** AWS no permite borrarlos. Quedan como registro y no cuestan nada.
- **Logs de CloudWatch** (`/aws/sagemaker/...`): ocupan muy poco. Si quieres, bórralos a mano en *CloudWatch → Log groups*.
- **Tu usuario de IAM** (`aws-train-admin`) y tu perfil de `aws login`: los vas a necesitar si repites el demo.

## Repetir el demo sin rehacer los guardarraíles

```bash
uv run python steps/99_teardown.py --keep-guardrails
```

Conserva el Budget y el Execution Role. Puedes volver a correr desde el paso 02.

## Verificar que no queda nada

Al final el script vuelve a preguntar por el tag e imprime lo que quede. Para comprobarlo tú mismo:

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=project,Values=aws-train \
  --profile aws-train --region us-east-1 \
  --query 'ResourceTagMappingList[].ResourceARN'
```

Lo único que debería aparecer son Training Jobs (`...:training-job/...`). Un recurso recién borrado puede seguir apareciendo unos minutos.
