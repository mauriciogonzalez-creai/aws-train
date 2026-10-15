# Paso 01 — Execution Role

```bash
uv run python steps/01_execution_role.py
```

## Qué hace

Crea el rol de IAM `aws-train-sagemaker-execution`, que **SageMaker asume** cuando entrena y cuando sirve el modelo. Le pone una política con permisos mínimos:

| Permiso | Para qué |
|---|---|
| Leer y escribir objetos en el bucket del demo (`aws-train-<cuenta>-<región>`) | Leer los datos de entrenamiento y guardar el `model.tar.gz` |
| Descargar imágenes de ECR | Bajar el contenedor de XGBoost que provee AWS |
| Escribir logs en CloudWatch (`/aws/sagemaker/*`) | Que puedas ver los logs del entrenamiento y del endpoint |
| Publicar métricas en CloudWatch | Métricas del Training Job |

Al final imprime el **ARN** del rol, que usan los pasos siguientes.

## Concepto clave: tus permisos vs. los de SageMaker

Hay dos identidades distintas:

- **Tú** (tu sesión de `aws login`): corres los scripts y le pides cosas a AWS.
- **SageMaker** (este rol): hace el trabajo dentro de AWS, con sus propios permisos.

Por eso tu sesión puede ser administradora y aun así un Training Job puede fallar por permisos: lo que falta está en este rol, no en tu usuario.

## Si lo vuelves a correr

Si el rol ya existe, se reutiliza. La política se vuelve a escribir siempre, así que correr el paso de nuevo arregla una política modificada a mano.

## Nota

IAM tarda unos segundos en propagar un rol nuevo. Si el paso 03 falla justo después con un error de que SageMaker no puede asumir el rol, espera un minuto y vuelve a intentarlo.

Siguiente: [paso 02 — subir los datos](step-02-upload-data.md).
