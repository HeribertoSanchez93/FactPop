$ErrorActionPreference = "Stop"

Write-Host "==> Running FactPop test suite..."
& .\.venv\Scripts\pytest -q --tb=short $args
