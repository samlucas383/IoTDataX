# Environment setup

This repo uses Docker Compose to run the IoT API, frontend, Postgres and Mosquitto.

Quick start (recommended):

1. Copy the example env file:

```powershell
copy .env.example .env
```

2. Edit `.env` if you need to change credentials or ports.

3. Start the stack:

```powershell
docker compose up --build -d
```

Helper scripts
----------------
There are helper scripts in `scripts/` to make it easy for contributors:

- `scripts/init-env.ps1` (PowerShell) - copies `.env.example` to `.env` if `.env` does not exist.
- `scripts/up.ps1` (PowerShell) - will create `.env` from the example if needed and run `docker compose up --build`.
- `scripts/up.sh` (Bash) - same as `up.ps1` for macOS/Linux.

Usage examples:

PowerShell:
```powershell
.\	ools\init-env.ps1    # optional: creates .env from .env.example
.\scripts\up.ps1        # creates .env if missing and runs compose
```

Bash:
```bash
./scripts/up.sh
```

4. View logs:

```powershell
docker compose logs -f iotapi
```

If you prefer not to create `.env`, the compose file has sane defaults; creating `.env` is optional but recommended for local overrides.

Swift service
-------------
The repository contains a simple Swift service at `services/Iotfrontend/swift-app` that builds with SwiftNIO.

Notes:
- The Dockerfile performs a multi-stage build using `swift:5.7` (builder) and `ubuntu:22.04` (runtime). The first build may take several minutes while Swift packages are fetched.
- The service is exposed on host port 8080 via `docker-compose.yml` as `swift-app`.

To build and run only the Swift service:

PowerShell / Bash:
```powershell
docker compose build swift-app
docker compose up -d swift-app
docker compose logs -f swift-app
```

If you edit Swift sources, rebuild with:
```powershell
docker compose build --no-cache swift-app
```

Note: Swift build artifacts are ignored by `.gitignore` to avoid committing large or platform-specific files.
