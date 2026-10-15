# Paso 03 — Entrenar con un Training Job

```bash
uv run python steps/03_train.py
```

> **Costo:** este es el primer paso que factura cómputo. El Training Job usa una instancia `ml.m5.xlarge` que AWS cobra **por segundo** mientras corre (normalmente unos minutos, incluido el arranque). Cuando termina, la instancia se apaga sola y deja de cobrar.

## Qué hace

1. Comprueba que existen la alerta de presupuesto (paso 00) y el Execution Role (paso 01).
2. Busca la imagen de **XGBoost que provee AWS** para tu región (versión `1.7-1`).
3. Lanza un **Training Job** con `ModelTrainer` (SDK v3):
   - lee `data/train.csv` y `data/validation.csv` del bucket,
   - entrena un clasificador binario (`objective = binary:logistic`, métrica `auc`, 100 rondas),
   - escribe el modelo entrenado en `s3://aws-train-<cuenta>-us-east-1/models/<job>/output/model.tar.gz`.
4. Muestra los logs del contenedor mientras entrena y espera a que termine.
5. Guarda el nombre del job y la ruta del modelo en `.aws-train-state.json`, que es lo que usa el paso 04.

## Qué pasa por dentro

```
tu terminal ──(ModelTrainer.train)──► SageMaker
                                        │ arranca una ml.m5.xlarge
                                        │ asume el Execution Role (paso 01)
                                        │ descarga la imagen de XGBoost (ECR de AWS)
                                        │ lee data/*.csv de S3
                                        │ entrena
                                        └► escribe model.tar.gz en S3 y apaga la instancia
```

No escribiste código de entrenamiento: el algoritmo ya viene dentro del contenedor de AWS (*Built-in algorithm*). Tú solo eliges la imagen, los datos y los hiperparámetros.

## Cómo leer los logs

Al final verás líneas como:

```
[99]#011train-auc:1.00000#011validation-auc:0.99...
```

`validation-auc` cerca de 1 significa que el modelo separa bien las dos clases en datos que no vio al entrenar.

## Si lo vuelves a correr

Si ya hay un Training Job completado, el paso **no entrena otra vez**: reutiliza el último modelo y te ahorra el costo. Para forzar un entrenamiento nuevo:

```bash
uv run python steps/03_train.py --retrain
```

Los Training Jobs terminados no se pueden borrar en AWS, pero tampoco cuestan nada: solo quedan como registro.

## Errores comunes

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Refusing to continue: Role aws-train-sagemaker-execution not found` | No corriste el paso 01 | `uv run python steps/01_execution_role.py` |
| `ResourceLimitExceeded` … `ml.m5.xlarge for training job usage` | Las cuentas nuevas pueden tener cuota 0 para esa instancia | Pide un aumento en *Service Quotas → Amazon SageMaker → ml.m5.xlarge for training job usage* (puede tardar días) |
| `ClientError` … `could not assume role` | IAM aún no propagó el rol recién creado | Espera un minuto y vuelve a correr |
| El job falla con `AccessDenied` sobre S3 o ECR | Al rol le falta un permiso | Revisa los logs en *CloudWatch → /aws/sagemaker/TrainingJobs* |

Siguiente: [paso 04 — desplegar el endpoint serverless](step-04-deploy-serverless.md).
