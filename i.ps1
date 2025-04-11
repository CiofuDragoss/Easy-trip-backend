& .\.venv\Scripts\Activate.ps1
Write-Host "venv activat"
uvicorn fapi.main:app --reload --host 0.0.0.0 --port 8000