# GenAI Guardrails Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-9%20passed-brightgreen.svg)](#testing)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

API-key-free, production-style Generative AI safety platform demonstrating
input guardrails, output guardrails, audit logging, adversarial evaluation,
metrics, containerization, and CI/CD.

## Features

- Prompt-injection and jailbreak blocking
- Restricted harmful-request blocking
- PII redaction
- API-key and credential redaction
- Toxicity signals
- Unsafe-output filtering
- Secret-leakage prevention
- Minimum-quality fallback
- High-impact disclaimer
- In-memory rate limiting
- JSONL audit logging
- Adversarial evaluation
- Streamlit dashboard
- FastAPI Swagger API
- 9 automated tests
- Docker and GitHub Actions

## Architecture

```text
Client
  ↓
Rate limiter
  ↓
Input guardrails
  ├─ Prompt injection
  ├─ Restricted content
  ├─ PII redaction
  ├─ Secret redaction
  └─ Toxicity
  ↓
Local deterministic provider
  ↓
Output guardrails
  ├─ Unsafe output
  ├─ Secret leakage
  ├─ Quality validation
  └─ High-impact disclaimer
  ↓
Safe response + audit event
```

## Tools

Python · FastAPI · Uvicorn · Pydantic · PyTest · HTTPX · Streamlit · Pandas ·
Docker · Docker Compose · GitHub Actions · JSONL audit logging

## Run

```powershell
cd C:\AI\genai-guardrails-platform
Set-ExecutionPolicy -Scope Process Bypass -Force
Unblock-File .\run_all.ps1
.\run_all.ps1
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Dashboard in a second terminal:

```powershell
cd C:\AI\genai-guardrails-platform
Set-ExecutionPolicy -Scope Process Bypass -Force
Unblock-File .\run_dashboard.ps1
.\run_dashboard.ps1
```

Dashboard:

```text
http://localhost:8501
```

## Endpoints

- `GET /health`
- `POST /chat`
- `POST /evaluate`
- `GET /guardrail-stats`

## Testing

```powershell
python -m pytest -v
```

Validated result:

```text
9 passed
```

## Docker

```powershell
docker compose up --build
```

Stop:

```powershell
docker compose down
```

## Demo evidence

### Screenshots

- [Docker Compose configuration](assets/demo/01-docker-compose-config.png)
- [FastAPI health check](assets/demo/02-fastapi-health-check.png)
- [Local validation — 9 tests passed](assets/demo/03-local-validation-tests.png)

### Videos

- [Automated evaluation](assets/demo/04-automated-evaluation.mp4)
- [Guardrails overview](assets/demo/05-guardrails-overview.mp4)
- [Guardrail status metrics](assets/demo/06-guardrail-status-metrics.mp4)
- [Harmful request blocked](assets/demo/07-harmful-request-blocked.mp4)
- [PII redaction](assets/demo/08-pii-redaction.mp4)
- [Prompt injection blocked](assets/demo/09-prompt-injection-blocked.mp4)
- [Safe redaction flow](assets/demo/10-safe-redaction-flow.mp4)
- [Safe request flow](assets/demo/11-safe-request-flow.mp4)
- [Streamlit dashboard](assets/demo/12-streamlit-dashboard.mp4)

## Repository details

**Name**

```text
genai-guardrails-platform
```

**Description**

```text
Production-style GenAI guardrails platform with prompt-injection blocking, PII and secret redaction, restricted-content controls, output validation, rate limiting, audit metrics, FastAPI, Streamlit, Docker, and CI/CD.
```

**Topics**

```text
generative-ai
ai-safety
llm-security
guardrails
prompt-injection
pii-redaction
secret-detection
fastapi
pydantic
streamlit
docker
github-actions
python
```

## Author

**Girish Vuyyuru**

- LinkedIn: https://www.linkedin.com/in/girish-genai-engineer
- GitHub: https://github.com/gireeshvuyyuru501-design
- Portfolio: https://gireeshvuyyuru501-design.github.io/Launch-AI-engineering-portfolio/

## License

MIT — see [LICENSE](LICENSE).
