# Create .env from .env.example if missing, then start docker compose
if (-not (Test-Path ".env")) {
  if (Test-Path ".env.example") {
    Copy-Item .env.example .env
    Write-Host ".env created from .env.example"
  } else {
    Write-Host "No .env.example present; create a .env file first"; exit 1
  }
} else {
  Write-Host ".env already exists"
}

Write-Host "Starting docker compose..."
docker compose up --build
