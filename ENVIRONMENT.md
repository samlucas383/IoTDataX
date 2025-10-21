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

4. View logs:

```powershell
docker compose logs -f iotapi
```

If you prefer not to create `.env`, the compose file has sane defaults; creating `.env` is optional but recommended for local overrides.
