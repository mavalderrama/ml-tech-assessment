# AceUp ML Tech Assessment — Transcript Analyzer API

This repository contains my implementation of the Python interview task: a small web API that analyzes plain text
transcripts and returns a concise summary plus actionable next steps. The design emphasizes clean (hexagonal)
architecture, clear separation of concerns, and testability.

As part of this excersise, I deployed the app to Google Cloud Run and used Terraform to manage infrastructure.
at https://aceup-demo-ml-engineer-261712848936.us-central1.run.app/docs

The min instance count is set to 0, so the app is free to scale down to 0 instances. What that said, you can expect
the app to be up and running after a few seconds after first cold request.

## What I built

- A FastAPI service with three main endpoints:
    - `POST /summary/generate` — Analyze a single transcript, store the result in memory, and return it with an ID.
    - `POST /summary/batch_generate` — Analyze multiple transcripts concurrently (async) in one request; stores and
      returns all results.
    - `GET /summary?id=...` — Retrieve a stored analysis by ID.
- Hexagonal architecture with explicit ports (interfaces) and adapters (OpenAI client and in-memory DB), and a service
  layer coordinating use-cases.
- Structured output from the LLM using Pydantic DTOs for safe, typed responses.
- In-memory storage with proper locking for both threaded and async paths.
- Automatic OpenAPI/Swagger docs via FastAPI.
- Unit tests for the service and adapters.

## Architecture overview (Hexagonal/Clean)

- Domain
    - DTOs: `app/domain/dtos.py` — typed models for requests and LLM responses.
    - Prompts: `app/domain/prompts.py` — system and user prompts templates.
    - Config: `app/domain/configurations.py` — environment-driven application settings.
- Ports (interfaces)
    - LLM port: `app/ports/llm.py` — abstract interface for LLM clients.
    - Repository port: `app/ports/repository.py` — abstract interface for persistence.
    - Manager port: `app/ports/manager.py` — interface for the service layer.
- Adapters (driving/driven)
    - OpenAI adapter: `app/adapters/openai.py` — implements `LLm` using OpenAI SDK with structured outputs.
    - In-memory DB: `app/adapters/db.py` — implements `Repository` with sync and async methods, guarded by locks.
- Services (application layer)
    - Controller: `app/services/controller.py` — implements `Manager`; orchestrates prompts, LLM calls, and persistence.
- Delivery (API)
    - FastAPI views: `app/views.py` — HTTP endpoints and request/response schemas.

Data flow example (single transcript):

1. Client POSTs a `Transcript` to `/summary/generate`.
2. `Controller.summarize` formats the prompt and invokes `OpenAIAdapter.run_completion` with DTO `LLMResponse`.
3. The adapter returns a parsed, typed model; the result is stored via the DB adapter, which adds a UUID.
4. The API returns `LLMResponseId` (summary, action_items, and id).

For batch processing, `Controller.asummarize` uses `asyncio.TaskGroup` to run multiple LLM calls concurrently, then
persists all results in bulk.

## Endpoints

- Health/root
    - `GET /` → `{ "message": "Hello AceUp" }`

- Generate single summary
    - `POST /summary/generate`
    - Request body (JSON):
      ```json
      { "text": "<your transcript text here>" }
      ```
    - Response (JSON):
      ```json
      {
        "id": "45d4d8e1-2f66-4d52-9c8e-5f4c6e83a9c9",
        "summary": "Concise overview of the transcript...",
        "action_items": ["Do X", "Schedule Y", "Prepare Z"]
      }
      ```

- Generate multiple summaries concurrently
    - `POST /summary/batch_generate`
    - Request body (JSON):
      ```json
      {
        "transcripts": [
          { "text": "first transcript..." },
          { "text": "second transcript..." }
        ]
      }
      ```
    - Response (JSON):
      ```json
      {
        "responses": [
          { "id": "...", "summary": "...", "action_items": ["..."] },
          { "id": "...", "summary": "...", "action_items": ["..."] }
        ]
      }
      ```

- Retrieve a summary by ID
    - `GET /summary?id=<UUID>`
    - Response (JSON): same shape as single generate.

Swagger/OpenAPI UI: visit `/docs` (Swagger) or `/redoc` after starting the app.

## Data contracts (DTOs)

Defined in `app/domain/dtos.py`:

- Request
    - `Transcript`: `{ text: str }` with validation (non-empty after trimming).
    - `Transcripts`: `{ transcripts: list[Transcript] }`.
- Response
    - `LLMResponse`: `{ summary: str, action_items: list[str] }`.
    - `LLMResponseId`: `LLMResponse` plus `{ id: UUID }`.
    - `LLMresponses`: `{ responses: list[LLMResponseId] }`.

## Prompts and structured outputs

- `app/domain/prompts.py` contains both the `SYSTEM_PROMPT` and `RAW_USER_PROMPT` template.
- The OpenAI adapter uses the SDK’s structured outputs (`beta.chat.completions.parse`) to return a Pydantic model
  instance described by `LLMResponse`. This ensures responses are well-typed and predictable.

## Configuration

- Settings live in `app/domain/configurations.py` using `pydantic-settings`.
- Environment variables:
    - `OPENAI_API_KEY` — your API key (required for real OpenAI calls).
    - `OPENAI_MODEL` — the model name, e.g. `gpt-4o-2024-08-06`.
- You can provide a `.env` file at the project root. Example:
  ```env
  OPENAI_API_KEY=sk-your-key
  OPENAI_MODEL=gpt-4o-2024-08-06
  ```
  Note: the settings loader is configured to look for `.env` relative to `project-root` (i.e., `app/.env`). In Docker
  Compose, variables come from the root `.env` via `env_file`, which works regardless of this path.

## How to run

### Prerequisites

- Python 3.14+
- Use `uv` (recommended; project includes `uv.lock`).

### Run locally (uv)

```bash
# From repo root
uv sync
uv run uvicorn app.views:app --host 0.0.0.0 --port 8000 --reload
```

Then open http://localhost:8000/docs

### Docker

With docker-compose (uses the included Dockerfile and `.env`):

```bash
docker compose up --build
```

## Testing

Tests are written with `pytest` and include unit tests for the OpenAI adapter (patched clients), the in-memory DB, and
the service controller.

```bash
uv run pytest -q
# or
pytest -q
```

## Design decisions and trade-offs

- Hexagonal architecture: Ports and adapters explicitly separate domain/service logic from infrastructure (LLM and
  persistence). This makes components easily swappable and unit-test friendly.
- Structured LLM outputs: Using Pydantic DTOs increases reliability and simplifies validation/serialization.
- In-memory persistence: Keeps the exercise self-contained and fast. It’s thread-safe and async-safe via locks, but not
  durable across restarts.
- Concurrency: Batch endpoint leverages `asyncio.TaskGroup` for clear, structured concurrency and proper error handling.
- Validation: `Transcript` enforces non-empty text. Additional validations (size limits, content checks) can be added as
  needed.
- Observability: Basic structured logging via Python’s logging.
- Simplicity over completeness: No authentication, rate limiting, or external database as per the scope.

## Limitations and possible improvements

- Persistence: Replace in-memory DB with a real database (Postgres/SQLite) and a migration tool.
- Robustness: Add retries/timeouts and circuit breakers around the LLM adapter; expose health/readiness endpoints.
- Security: Add request authentication and audit logging; validate payload sizes; consider PII handling.
- Product UX: Extend the schema with confidence scores or categories; add pagination and search over stored summaries.
- Testing: Add integration tests hitting the actual HTTP layer and JSON schemas; consider property-based tests for DTO
  validation.
- Config: Expand settings (timeouts, max batch size, rate-limits), and standardize env var loading path.

## Repository layout

```
.
├── app
│   ├── adapters
│   │   ├── db.py
│   │   └── openai.py
│   ├── domain
│   │   ├── configurations.py
│   │   ├── dtos.py
│   │   └── prompts.py
│   ├── ports
│   │   ├── llm.py
│   │   ├── manager.py
│   │   └── repository.py
│   ├── services
│   │   └── controller.py
│   └── views.py
├── tests
│   ├── adapters
│   └── services
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md (this file)
```

## Example cURL

- Single generate

```bash
curl -X POST http://localhost:8000/summary/generate \
  -H 'Content-Type: application/json' \
  -d '{"text": "Today we discussed quarterly goals and identified blockers."}'
```

- Get by id

```bash
curl 'http://localhost:8000/summary?id=45d4d8e1-2f66-4d52-9c8e-5f4c6e83a9c9'
```

- Batch generate

```bash
curl -X POST http://localhost:8000/summary/batch_generate \
  -H 'Content-Type: application/json' \
  -d '{"transcripts": [{"text": "A"}, {"text": "B"}]}'
```

## Notes

- The app will start and respond even without a real `OPENAI_API_KEY`, but the OpenAI-backed paths require a valid key
  in real usage.
- FastAPI automatically serves interactive docs at `/docs` once the server is running.

## Deployment (GCP Cloud Run via Terraform)

This repo includes infrastructure-as-code to deploy the API to Google Cloud Run using Terraform. The Terraform files
live in `deployment/`:

- `provider.tf` — configures the Google provider using a service account key file
- `variables.tf` — inputs such as `project_id`, `region`, `service_name`, and `container_image`
- `main.tf` — defines a `google_cloud_run_v2_service` and makes it publicly invokable
- `outputs.tf` — prints the deployed service URL (`cloud_run_url`)
- `terraform.tfvars` — example values you can modify

Important notes:

- The sample uses min instances `0` and max `1` to minimize cost; traffic is public (`roles/run.invoker` for
  `allUsers`).
- Environment variables (e.g., `OPENAI_API_KEY`) are not set by default in Terraform. See “Set environment variables”
  below.
- The sample provider authenticates using a JSON key file. For production, prefer Workload Identity and a remote
  Terraform backend (GCS) for state.

### Prerequisites

- A GCP project and billing enabled
- IAM permissions to deploy Cloud Run and Artifact Registry (e.g., roles/run.admin, roles/artifactregistry.admin,
  roles/iam.serviceAccountUser)
- CLIs installed: `gcloud`, `docker`, and `terraform`
- A service account JSON key with sufficient privileges (used by Terraform), or switch to ADC/Workload Identity (not
  shown here)

Enable required APIs (once per project):

```bash
PROJECT_ID=<your-project-id>
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project "$PROJECT_ID"
```

### 1) Build and push the container to Artifact Registry

Create a Docker repository if you don’t have one yet:

```bash
REGION=us-central1
REPO=aceup-demo
PROJECT_ID=<your-project-id>
# create a Docker repo (no-op if it already exists)
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Transcript API images" \
  --project "$PROJECT_ID"
```

Authenticate Docker to Artifact Registry and build/push the image:

```bash
REGION=us-central1
PROJECT_ID=<your-project-id>
REPO=aceup-demo
IMAGE=app
TAG=latest
REG_HOST="$REGION-docker.pkg.dev"
IMAGE_URI="$REG_HOST/$PROJECT_ID/$REPO/$IMAGE:$TAG"

# authenticate Docker
gcloud auth configure-docker "$REG_HOST"

# build (optionally pass your key at build time if you bake it into the image — not recommended for production)
docker build -t "$IMAGE_URI" --build-arg OPENAI_API_KEY="$OPENAI_API_KEY" .

# push
docker push "$IMAGE_URI"
```

You can also host the image elsewhere (Docker Hub, other registries); just set `container_image` accordingly in
Terraform.

### 2) Configure Terraform variables

Open `deployment/terraform.tfvars` and set the values to your environment. Example:

```hcl
project_id      = "jupyter-247316"
region          = "us-central1"
zone            = "us-central1-a"
container_image = "us-central1-docker.pkg.dev/jupyter-247316/aceup-demo/app:latest"
# Optional: credentials_file can be overridden; default is "gcp_key.json" in the deployment/ folder
# credentials_file = "/path/to/your-service-account.json"
```

Security note: a sample `gcp_key.json` file is included in `deployment/` for demonstration. In real projects, do NOT
commit key files; prefer Workload Identity or store keys in a secure secret manager and use a locked-down CI
environment.

### 3) Deploy with Terraform

From the repository root:

```bash
cd deployment
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

On success, Terraform prints the Cloud Run URL:

```text
Outputs:
cloud_run_url = "https://<service>-<hash>-<region>.a.run.app"
```

### 4) Set environment variables on Cloud Run

The app needs `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`). You can set them after the first deploy using `gcloud`:

```bash
SERVICE_NAME=<your-cloud-run-service-name>   # must match var.service_name in Terraform (default: aceup-demo-ml-engineer)
REGION=<your-region>                         # e.g., us-central1
PROJECT_ID=<your-project-id>

# Set env vars
gcloud run services update "$SERVICE_NAME" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --set-env-vars OPENAI_API_KEY="$OPENAI_API_KEY",OPENAI_MODEL="gpt-4o-2024-08-06"
```

### 5) Verify the deployment

Grab the URL from Terraform output and check health and docs:

```bash
URL=$(terraform output -raw cloud_run_url)

# Health
curl -s "$URL/" | jq .

# Swagger UI should be available
open "$URL/docs"  # macOS; use xdg-open on Linux
```

Try an example request (requires a valid `OPENAI_API_KEY` set on the service):

```bash
curl -X POST "$URL/summary/generate" \
  -H 'Content-Type: application/json' \
  -d '{"text": "Today we discussed quarterly goals and identified blockers."}'
```

### 6) Cleanup

To remove the Cloud Run service and related IAM binding:

```bash
cd deployment
terraform destroy
```

You may also want to delete pushed images:

```bash
REGION=us-central1
PROJECT_ID=<your-project-id>
REPO=aceup-demo
IMAGE=app
TAG=latest
REG_HOST="$REGION-docker.pkg.dev"
IMAGE_URI="$REG_HOST/$PROJECT_ID/$REPO/$IMAGE:$TAG"

gcloud artifacts docker images delete "$IMAGE_URI" --delete-tags --quiet --project "$PROJECT_ID"
```

### Additional guidance

- State management: the example uses local Terraform state. For teams, use a remote backend (e.g., GCS) with proper
  locking.
- Access control: the sample makes the service public; restrict to authenticated invokers in production.
- Costs: with `min_instance_count = 0`, you may see cold starts. Increase as needed.
- Observability: consider adding Cloud Logging/Monitoring dashboards and a `/healthz` endpoint.
