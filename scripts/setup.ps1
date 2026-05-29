# Bootstrap script for the Personalized Learning Assistant.
# Run from the project root:  .\scripts\setup.ps1

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing requirements into .venv..."
& ".venv\Scripts\python.exe" -m pip install --upgrade pip
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "Copying .env.example -> .env"
    Copy-Item ".env.example" ".env"
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Next steps:"
Write-Host "  1. ollama pull llama3.1:8b"
Write-Host "  2. .venv\Scripts\python.exe scripts\generate_demo_pdfs.py"
Write-Host "  3. .venv\Scripts\python.exe scripts\ingest_documents.py"
Write-Host "  4. .venv\Scripts\uvicorn.exe app.main:app --reload"
Write-Host "  5. (another terminal) .venv\Scripts\streamlit.exe run frontend\streamlit_app.py"
