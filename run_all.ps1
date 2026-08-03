$ErrorActionPreference = "Stop"

Write-Host "Preparing GenAI Guardrails Platform..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            python -m venv .venv
        }
    }
    else {
        python -m venv .venv
    }
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

python -m pytest -v

Write-Host ""
Write-Host "Tests passed. Starting FastAPI..." -ForegroundColor Green
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host "Dashboard in a second terminal: .\run_dashboard.ps1"

python -m uvicorn app.main:app --reload --port 8000
