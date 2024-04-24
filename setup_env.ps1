$envPath = ".\env"
if (-Not (Test-Path $envPath)) {
    python -m venv $envPath
}
& $envPath\Scripts\Activate.ps1
python -m pip install -r requirements.txt