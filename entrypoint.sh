#!/usr/bin/env sh
echo "[entrypoint/INFO] Initialising"
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "[entrypoint/INFO] Running migrations"
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "[entrypoint/ERROR] DATABASE_URL is not set"
    exit 1
  fi
  piccolo migrations forwards nephthys --trace
else
  echo "[entrypoint/WARN] NOT running migrations"
fi

echo "[entrypoint/INFO] Starting Nephthys"
exec nephthys
