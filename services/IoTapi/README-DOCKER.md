# Building a Docker image for IoTapi

This document shows how to build and run a Docker image for the IoTapi service.

Quick build and run (from repository root):

```powershell
# Build the image (tag it as iotapi:latest)
docker build -t iotapi:latest -f services/IoTapi/Dockerfile .

# Run the container (map port 8000)
docker run --rm -p 8000:8000 iotapi:latest
```

Notes:
- The Dockerfile expects your Python entrypoint to be either a FastAPI/ASGI app named `app` in `app.py` (so `uvicorn app:app` works), or a `main.py` script with a `if __name__ == '__main__'` entrypoint. If your project uses different filenames or a different server (gunicorn, flask CLI, etc.), update the `CMD` line in the Dockerfile accordingly.
- `requirements.txt` is used during image build. If you don't have one, create it by running your venv's `python -m pip freeze > requirements.txt` locally.
- The Dockerfile installs `build-essential` and `gcc` to allow compiling wheels if some Python packages require it. Remove them if you don't need them to slim the image.

If you'd like, I can:
- Detect your actual app entrypoint and update the Dockerfile CMD to the correct start command.
- Add a small sample `app.py` (FastAPI) or `main.py` scaffold so the image runs out-of-the-box.
