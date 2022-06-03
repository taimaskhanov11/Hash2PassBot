#!/usr/bin/env bash
poetry run uvicorn api_server:app --port 8001 --app-dir=hash2passbot/apps/api &
poetry run python hash2passbot/main.py && fg
