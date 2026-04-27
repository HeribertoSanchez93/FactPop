$ErrorActionPreference = "Stop"

Write-Host "==> Verifying Python 3.13..."
$pyVersion = python --version 2>&1
if ($pyVersion -notmatch "3\.13") {
    Write-Error "Python 3.13 required. Found: $pyVersion. Install it from https://python.org"
    exit 1
}
Write-Host "    $pyVersion"

Write-Host "==> Creating .venv..."
python -m venv .venv

Write-Host "==> Activating .venv..."
& .\.venv\Scripts\Activate.ps1

Write-Host "==> Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "==> Copying .env.example -> .env (fill in FACTPOP_API_KEY before running)..."
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "ACTION REQUIRED: Open .env and set your FACTPOP_API_KEY."
} else {
    Write-Host "==> .env already exists, skipping copy."
}

Write-Host ""
Write-Host "Setup complete!"
Write-Host "  Activate venv : .\.venv\Scripts\Activate.ps1"
Write-Host "  Run daemon     : python -m factpop"
Write-Host "  Run CLI        : python -m factpop.app.cli --help"
