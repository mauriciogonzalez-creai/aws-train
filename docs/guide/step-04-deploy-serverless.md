# Paso 04 — Desplegar el endpoint serverless

```bash
uv run python steps/04_deploy_serverless.py
```

> **Costo:** un **Serverless Endpoint** cobra por petición y por el tiempo que procesa cada una. Mientras nadie lo llama, escala a cero y no cobra cómputo. Aun así, bórralo al terminar con el [paso 99](step-99-teardown.md).

## Qué hace

Crea tres recursos de SageMaker, en este orden, todos con el tag `project=aws-train`:

| Recurso | Nombre | Qué es |
|---|---|---|
| **SageMaker Model** | `aws-train-xgb-model` | Une tres cosas: el `model.tar.gz` del paso 03, la imagen de XGBoost y el Execution Role |
| **Endpoint Configuration** | `aws-train-serverless` | Dice **cómo** servir el modelo: serverless, 2048 MB de memoria, máximo 1 petición simultánea |
| **Endpoint** | `aws-train-serverless` | La URL HTTPS que recibe peticiones y devuelve predicciones |

Después espera a que el endpoint quede en estado `InService` (normalmente unos minutos) y guarda su nombre en `.aws-train-state.json`.

## Por qué tres recursos y no uno

Cada uno cambia por motivos distintos:

- **Model**: cambia cuando reentrenas (otro `model.tar.gz`).
- **Endpoint Configuration**: cambia cuando quieres más memoria, otra concurrencia o pasar a instancias dedicadas.
- **Endpoint**: es estable; lo actualizas apuntándolo a otra configuración sin cambiar su nombre ni su URL.

En el SDK v3 los creas explícitamente con `Model.create`, `EndpointConfig.create` y `Endpoint.create` de `sagemaker.core.resources`. Los tutoriales de v2 lo esconden detrás de un único `estimator.deploy(...)`.

## Si lo vuelves a correr

Cada recurso que ya existe se reutiliza. Si reentrenaste con `--retrain`, el Model existente **sigue apuntando al modelo viejo**: corre el [paso 99](step-99-teardown.md) y luego este paso otra vez.

## Errores comunes

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Refusing to continue: No trained model found` | Falta `.aws-train-state.json` o no corriste el paso 03 | `uv run python steps/03_train.py` (reutiliza el job si ya existe) |
| El endpoint termina en `Failed` | El contenedor no pudo cargar el modelo o al rol le falta un permiso | Revisa *CloudWatch → /aws/sagemaker/Endpoints/aws-train-serverless* |
| `ResourceLimitExceeded` … serverless | Cuota de memoria o concurrencia serverless | *Service Quotas → Amazon SageMaker* |

Siguiente: [paso 05 — llamar al endpoint](step-05-invoke-serverless.md).
