#!/usr/bin/env bash
poetry run uvicorn api_server:app --port 8001 --app-dir=hash2passbot/api &
poetry run python user_database_tg/main.py && fg
