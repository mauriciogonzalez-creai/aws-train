# Paso 05 — Llamar al endpoint

```bash
uv run python steps/05_invoke_serverless.py
```

## Qué hace

Toma 5 filas del conjunto de **validación** (datos que el modelo no vio al entrenar), le quita la etiqueta a cada una, la manda al endpoint como CSV y mide cuánto tarda cada llamada:

```
label=1 predicted=1 probability=0.987 latency=4210 ms
label=0 predicted=0 probability=0.031 latency=95 ms
...
First call (may include cold start): 4210 ms
Warm calls median over 4: 92 ms
```

- `probability` es lo que devuelve XGBoost: la probabilidad de la clase 1.
- `predicted` aplica un umbral de 0.5.
- Los números de arriba son ilustrativos; los tuyos van a variar.

## El cold start

La **primera** llamada después de un rato sin tráfico tarda segundos, no milisegundos. El endpoint serverless había escalado a cero y AWS tiene que arrancar el contenedor y cargar el modelo. Las siguientes llamadas ya lo encuentran despierto.

No es un error: es el precio de no pagar mientras nadie lo usa.

## Serverless vs. Real-time: ¿cuándo usar cada uno?

Este demo solo crea endpoints **serverless** (ADR-003). En producción, la otra opción común es un **Real-time Endpoint** sobre una instancia dedicada.

| | Serverless | Real-time |
|---|---|---|
| Cobro | Por petición y tiempo de proceso; cero en reposo | Por hora mientras exista, aunque nadie lo llame |
| Primera llamada | Puede tener cold start (segundos) | Siempre caliente |
| Tráfico ideal | Esporádico o impredecible, demos, herramientas internas | Constante, o con requisitos estrictos de latencia |
| Hardware | Solo CPU, memoria limitada | Cualquier instancia, incluidas GPU |
| Riesgo en una cuenta personal | Bajo | Alto: si olvidas borrarlo, sigue cobrando cada hora |

Regla práctica: empieza serverless. Cámbiate a real-time cuando el cold start moleste a usuarios reales o cuando el tráfico sea tan constante que pagar por hora salga más barato.

## Errores comunes

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Refusing to continue: Endpoint aws-train-serverless not found` | No corriste el paso 04 | `uv run python steps/04_deploy_serverless.py` |
| `PredictionError: Expected a probability` | El endpoint respondió algo que no es un número entre 0 y 1 | Revisa que el CSV no lleve la etiqueta ni encabezado |
| `ModelError` | El contenedor devolvió un error | *CloudWatch → /aws/sagemaker/Endpoints/aws-train-serverless* |

Cuando termines, borra todo: [paso 99 — teardown](step-99-teardown.md).
