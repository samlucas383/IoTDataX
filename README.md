# IoTDataX

This repository contains a small example IoT project with two services:

- `services/IoTApi` — Python API service (placeholder `main.py` present)
- `services/Iotfrontend/iot-react-app` — React frontend built with Create React App

The repo includes Dockerfiles for both services and a `docker-compose.yml` to run the full stack together with PostgreSQL and Eclipse Mosquitto (MQTT broker).

Contents
--------
- `services/IoTApi/` — backend service (Python)
- `services/Iotfrontend/iot-react-app/` — frontend (React)
- `docker-compose.yml` — builds and runs backend, frontend, postgres, mosquitto
- `.env.example` — repo-level environment example (copy to `.env`)
- `ENVIRONMENT.md` — environment / quick start docs
- `scripts/` — helper scripts (`init-env.ps1`, `up.ps1`, `up.sh`) to create `.env` and start the stack

Quick start (recommended)
-------------------------
1. Copy the example env file (only once):

PowerShell:
```powershell
copy .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

2. Start the stack (build images if needed):

```powershell
docker compose up --build -d
```

3. Confirm services:

```powershell
docker compose ps
docker compose logs -f
```

Access
------
- Frontend (nginx): http://localhost:3000
- Backend: http://localhost:8000
- Postgres: localhost:5432 (user: iotuser, pass: iotpass, db: iotdb)
- Mosquitto (MQTT): 1883 (optional websocket: 9001)

Developer setup (Python)
------------------------
If you're contributing to the Python service, use a virtualenv locally (do NOT commit `.venv`):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r services/IoTApi/requirements.txt
```

If `requirements.txt` is empty, install the packages you need and then run `pip freeze > services/IoTApi/requirements.txt`.

Mosquitto configuration
-----------------------
By default the compose file uses Docker-managed named volumes for Mosquitto data/config. If you want custom config or persistent config files you can:

1. Create a host folder `services/mosquitto/config` and `services/mosquitto/data`
2. Add a `mosquitto.conf` in `services/mosquitto/config`
3. Update `docker-compose.yml` to bind mount those folders instead of using named volumes.

Postgres access
---------------
Use `docker exec` to run psql inside the postgres container:

```powershell
docker exec -it iot-postgres psql -U iotuser -d iotdb
```

Or connect using a host client to localhost:5432 with the same credentials.

Troubleshooting
---------------
- Compose errors about missing `.env`: copy `.env.example` to `.env` or run `./scripts/up.ps1` (PowerShell) / `./scripts/up.sh` (bash) which will create `.env` if missing and start compose.
- If ports are in use, edit `.env` or adjust `docker-compose.yml` port mappings.
- If the backend needs dependencies, populate `services/IoTApi/requirements.txt` before building the image.

Contributing
------------
- Don't commit `.venv` or other local environment artifacts. Use `requirements.txt` or Docker for reproducibility.
- Add a clear migration path (Alembic / Django migrations) if the backend schema changes.

If you'd like, I can also add a `make` file or PowerShell task to automate common developer tasks (build, test, start). Open to suggestions.
