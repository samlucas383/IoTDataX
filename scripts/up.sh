#!/usr/bin/env bash
set -euo pipefail
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo ".env created from .env.example"
  else
    echo "No .env.example present; create .env first" >&2
    exit 1
  fi
else
  echo ".env already exists"
fi

echo "Starting docker compose..."
docker compose up --build
