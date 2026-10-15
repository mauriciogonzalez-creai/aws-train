# 00 — Prerrequisitos

Antes de correr cualquier paso necesitas cuatro cosas: una cuenta de AWS, un usuario de IAM, la AWS CLI con `aws login` y `uv`. Esta página te lleva de cero a un perfil de AWS funcionando.

> **Costo:** esta página no crea nada facturable. El primer recurso con costo potencial aparece en el paso 03 (Training Job), y el paso 00 crea antes una alerta de presupuesto.

## 1. Cuenta de AWS personal

1. Crea una cuenta en <https://aws.amazon.com/> con tu correo personal. AWS pide una tarjeta aunque uses el free tier.
2. Activa MFA en el usuario root (*IAM → Security credentials → Assign MFA*).
3. No uses el usuario root para nada más. A partir de aquí trabajas con un usuario de IAM.

## 2. Usuario de IAM para trabajar

Usamos credenciales temporales en vez de access keys permanentes: si alguien copia tu `~/.aws`, las credenciales caducan solas (ADR-002).

1. Entra como root y abre **IAM → Users → Create user**. Nómbralo, por ejemplo, `aws-train-admin`.
2. Marca **Provide user access to the AWS Management Console** y define una contraseña.
3. En permisos, elige **Attach policies directly** y adjunta estas dos políticas administradas:
   - `AdministratorAccess` — es una cuenta personal de laboratorio; en una cuenta compartida usarías permisos más acotados.
   - `SignInLocalDevelopmentAccess` — permite que `aws login` le entregue credenciales temporales a la CLI.
4. Abre el usuario recién creado → **Security credentials → Assign MFA device** y activa MFA.
5. **No crees access keys.** No las necesitas.

> **¿Por qué no IAM Identity Center?** Es lo que AWS recomienda para empresas, pero en una cuenta personal exige activar AWS Organizations, y en nuestra primera prueba ese paso se bloqueó pidiendo el correo de una "management account". `aws login` da el mismo beneficio (credenciales temporales) sin esa configuración.

## 3. AWS CLI y `aws login`

1. Instala o actualiza la AWS CLI v2: <https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>. Necesitas la **versión 2.32.0 o mayor**:

   ```bash
   aws --version
   ```

2. Inicia sesión y crea el perfil:

   ```bash
   aws login --profile aws-train
   ```

   La primera vez te pregunta la región: escribe `us-east-1`. Luego abre el navegador: entra con el usuario `aws-train-admin` (no con root) y su MFA.

3. Comprueba que funciona:

   ```bash
   aws sts get-caller-identity --profile aws-train
   ```

   Debe mostrar tu número de cuenta. Las credenciales se renuevan solas hasta por 12 horas. Si un paso falla más adelante con un error de credenciales expiradas, vuelve a entrar con:

   ```bash
   aws login --profile aws-train
   ```

## 4. Python y dependencias con uv

1. Instala `uv`: <https://docs.astral.sh/uv/getting-started/installation/>
2. Desde la raíz del repo:

   ```bash
   uv sync
   uv run pytest
   ```

   `uv sync` descarga Python 3.12 si no lo tienes y crea `.venv/` con las versiones exactas de `uv.lock`. Incluye `boto3[crt]`, que es lo que permite a los scripts de Python usar el perfil de `aws login`.

### Versión del SDK de SageMaker

El demo fija **SageMaker Python SDK v3** (`sagemaker>=3,<4`, ADR-001). La mayoría de los tutoriales en internet todavía usan v2, que tiene otra API y ya está en camino de deprecación. Si copias un ejemplo, revisa de qué versión es:

| Si ves esto… | Es v2 | En este demo (v3) se usa… |
|---|---|---|
| `from sagemaker.estimator import Estimator` y `.fit()` | sí | `from sagemaker.train import ModelTrainer` y `.train()` |
| `estimator.deploy(...)` / `Predictor` | sí | `Model`, `EndpointConfig` y `Endpoint` de `sagemaker.core.resources` |
| `sagemaker.image_uris.retrieve` | sí | `sagemaker.core.image_uris.retrieve` |

## 5. Variables de entorno

Los pasos leen su configuración del entorno:

| Variable | Obligatoria | Default | Para qué |
|---|---|---|---|
| `AWS_PROFILE` | sí | — | El perfil del punto 3 (`aws-train`) |
| `BUDGET_EMAIL` | sí | — | Correo que recibe la alerta de presupuesto |
| `AWS_REGION` | no | `us-east-1` | Región; la guía solo está verificada en `us-east-1` |
| `BUDGET_LIMIT_USD` | no | `10` | Límite mensual de la alerta, en dólares |

La forma más cómoda es un archivo `.env` en la raíz del repo, que los pasos leen solos:

```bash
cp .env.example .env
# edita .env y pon tu correo en BUDGET_EMAIL
```

`.env` está en `.gitignore`: tu correo no se sube al repo. Los pasos lo buscan en la carpeta desde donde los corres, así que córrelos siempre desde la raíz del repo.

Si prefieres no usar el archivo, también puedes exportar las variables en la terminal (tienen prioridad sobre `.env`):

```bash
export AWS_PROFILE=aws-train
export BUDGET_EMAIL=tu-correo@ejemplo.com
```

Listo: sigue con el [paso 00 — alerta de presupuesto](step-00-budget.md).
