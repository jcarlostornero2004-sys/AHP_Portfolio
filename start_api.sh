#!/bin/bash
# Starts the FastAPI backend using the system Python (with uvicorn installed).
# This bypasses the .venv which does not have uvicorn.

UVICORN="$HOME/AppData/Local/Python/pythoncore-3.14-64/Scripts/uvicorn.exe"

# Fallback: try finding uvicorn in common locations
if [ ! -f "$UVICORN" ]; then
  UVICORN=$(find "$HOME/AppData/Local/Python" -name "uvicorn.exe" 2>/dev/null | head -1)
fi

if [ -z "$UVICORN" ] || [ ! -f "$UVICORN" ]; then
  echo "[API] ERROR: No se encontró uvicorn.exe. Instálalo con: pip install uvicorn"
  exit 1
fi

cd "$(dirname "$0")/apps/api"
echo "[API] Arrancando con $UVICORN"
exec "$UVICORN" main:app --reload --host 127.0.0.1 --port 8000
