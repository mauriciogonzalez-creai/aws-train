# Paso 02 — Subir los datos a S3

```bash
uv run python steps/02_upload_data.py
```

## Qué hace

1. Comprueba que existe la alerta de presupuesto del paso 00. Si no existe, se niega a continuar.
2. Crea el bucket de S3 `aws-train-<tu-cuenta>-us-east-1` con el tag `project=aws-train`.
3. Carga el dataset público **breast cancer** de scikit-learn (569 filas, 30 columnas numéricas, etiqueta 0/1), lo divide en entrenamiento (80 %) y validación (20 %) y sube dos archivos:

```
s3://aws-train-<cuenta>-us-east-1/
└── data/
    ├── train.csv
    └── validation.csv
```

## El formato que pide XGBoost

El contenedor de XGBoost que provee AWS espera un CSV muy concreto:

- **sin encabezado**,
- **la etiqueta en la primera columna**,
- el resto, las variables numéricas.

Una fila se ve así (recortada):

```
0,17.99,10.38,122.8,1001.0,0.1184,...
```

El `0` inicial es la etiqueta. Si mandas un CSV con encabezado, el entrenamiento falla o, peor, aprende de la fila de nombres.

## Conceptos

- **S3** guarda archivos (objetos) dentro de un **bucket**. El nombre del bucket es único en todo AWS; por eso lleva tu número de cuenta.
- El bucket solo guarda archivos: los datos y, después del paso 03, el modelo entrenado (`model.tar.gz`). El entrenamiento y el endpoint viven en SageMaker.
- Guardar unos KB en S3 cuesta prácticamente nada.

## Si lo vuelves a correr

Reutiliza el bucket y vuelve a subir los mismos archivos: la división es determinista, así que el contenido no cambia.

## Errores comunes

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Refusing to continue: Budget aws-train-budget not found` | No corriste el paso 00 | `uv run python steps/00_budget.py` |
| `AccessDenied` al crear el bucket | Tu usuario no tiene permisos de S3 | Revisa que tenga `AdministratorAccess` (guía 00, sección 2) |

Siguiente: [paso 03 — entrenar](step-03-train.md).
